from post_service.protos import posts_pb2, posts_pb2_grpc
from post_service.app.models import Post, PostView, PostLike, PostComment
from post_service.app.kafka_producer import kafka_producer
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import StatusCode
import grpc
from tortoise.exceptions import DoesNotExist, IntegrityError

class PostService(posts_pb2_grpc.PostServiceServicer):

    async def CreatePost(self, request, context):
        post = await Post.create(
            title=request.title,
            description=request.description,
            author_id=request.author_id,
            is_private=request.is_private,
            tags=list(request.tags)
        )
        return posts_pb2.PostResponse(post=self._format_post_message(post))

    async def GetPost(self, request, context):
        post = await Post.get_or_none(id=request.id)
        if not post:
            await context.abort(StatusCode.NOT_FOUND, "Post not found")
            return posts_pb2.PostResponse()
        
        if post.is_private and post.author_id != request.requester_id:
            await context.abort(StatusCode.PERMISSION_DENIED, "You are not allowed to view this post")
            return posts_pb2.PostResponse()
            
        return posts_pb2.PostResponse(post=self._format_post_message(post))

    async def UpdatePost(self, request, context):
        post = await Post.get_or_none(id=request.id)
        if not post:
            await context.abort(StatusCode.NOT_FOUND, "Post not found")
            return posts_pb2.PostResponse()

        if post.author_id != request.requester_id:
            await context.abort(StatusCode.PERMISSION_DENIED, "You are not the author of this post")
            return posts_pb2.PostResponse()

        update_data = {
            "title": request.title,
            "description": request.description,
            "is_private": request.is_private,
            "tags": list(request.tags),
        }
        await post.update_from_dict(update_data).save()
        
        return posts_pb2.PostResponse(post=self._format_post_message(post))

    async def DeletePost(self, request, context):
        post = await Post.get_or_none(id=request.id)
        if not post:
            await context.abort(StatusCode.NOT_FOUND, "Post not found")
            return posts_pb2.DeletePostResponse()
        
        if post.author_id != request.requester_id:
            await context.abort(StatusCode.PERMISSION_DENIED, "You are not the author of this post")
            return posts_pb2.DeletePostResponse()
            
        await post.delete()
        return posts_pb2.DeletePostResponse()

    async def ListPosts(self, request, context):
        page = request.page or 1
        page_size = request.page_size or 10
        offset = (page - 1) * page_size

        posts_query = Post.filter(is_private=False)
        total_count = await posts_query.count()
        posts = await posts_query.offset(offset).limit(page_size).order_by("-created_at")
        
        post_messages = [self._format_post_message(p) for p in posts]

        return posts_pb2.ListPostsResponse(
            posts=post_messages,
            total_count=total_count,
            page=page,
            page_size=page_size
        )

    def _format_post_message(self, post: Post):
        created_at_ts = Timestamp()
        if post.created_at:
            created_at_ts.FromDatetime(post.created_at)
        
        updated_at_ts = Timestamp()
        if post.updated_at:
            updated_at_ts.FromDatetime(post.updated_at)
        
        return posts_pb2.Post(
            id=str(post.id),
            title=post.title,
            description=post.description,
            author_id=post.author_id,
            created_at=created_at_ts,
            updated_at=updated_at_ts,
            is_private=post.is_private,
            tags=post.tags,
        )

    async def ViewPost(self, request, context):
        try:
            try:
                post = await Post.get_or_none(id=request.post_id)
            except ValueError:
                await context.abort(StatusCode.INVALID_ARGUMENT, "Invalid post ID format")
                return posts_pb2.ViewPostResponse()
                
            if not post:
                await context.abort(StatusCode.NOT_FOUND, "Post not found")
                return posts_pb2.ViewPostResponse()
            
            if post.is_private and post.author_id != request.user_id:
                await context.abort(StatusCode.PERMISSION_DENIED, "You are not allowed to view this post")
                return posts_pb2.ViewPostResponse()
            
            view, created = await PostView.get_or_create(
                post_id=post.id,
                user_id=request.user_id
            )
            
            kafka_producer.send_post_view_event(str(post.id), request.user_id)
            
            return posts_pb2.ViewPostResponse(
                success=True,
                message="Post viewed successfully"
            )
            
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {str(e)}")
            return posts_pb2.ViewPostResponse()

    async def LikePost(self, request, context):
        try:
            post = await Post.get_or_none(id=request.post_id)
            if not post:
                await context.abort(StatusCode.NOT_FOUND, "Post not found")
                return posts_pb2.LikePostResponse()
            
            try:
                await PostLike.create(
                    post_id=post.id,
                    user_id=request.user_id
                )
                
                kafka_producer.send_post_like_event(str(post.id), request.user_id, "like")
                
                total_likes = await PostLike.filter(post_id=post.id).count()
                
                return posts_pb2.LikePostResponse(
                    success=True,
                    message="Post liked successfully",
                    total_likes=total_likes
                )
                
            except IntegrityError:
                await context.abort(StatusCode.ALREADY_EXISTS, "You have already liked this post")
                return posts_pb2.LikePostResponse()
                
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {str(e)}")
            return posts_pb2.LikePostResponse()

    async def UnlikePost(self, request, context):
        try:
            post = await Post.get_or_none(id=request.post_id)
            if not post:
                await context.abort(StatusCode.NOT_FOUND, "Post not found")
                return posts_pb2.UnlikePostResponse()
            
            like = await PostLike.get_or_none(post_id=post.id, user_id=request.user_id)
            if like:
                await like.delete()
                
                kafka_producer.send_post_like_event(str(post.id), request.user_id, "unlike")
                
                total_likes = await PostLike.filter(post_id=post.id).count()
                
                return posts_pb2.UnlikePostResponse(
                    success=True,
                    message="Post unliked successfully",
                    total_likes=total_likes
                )
            else:
                await context.abort(StatusCode.NOT_FOUND, "You haven't liked this post")
                return posts_pb2.UnlikePostResponse()
                
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {str(e)}")
            return posts_pb2.UnlikePostResponse()

    async def CommentPost(self, request, context):
        try:
            post = await Post.get_or_none(id=request.post_id)
            if not post:
                await context.abort(StatusCode.NOT_FOUND, "Post not found")
                return posts_pb2.CommentPostResponse()
            
            comment = await PostComment.create(
                post_id=post.id,
                user_id=request.user_id,
                content=request.content
            )
            
            kafka_producer.send_post_comment_event(str(post.id), request.user_id, comment.id, request.content)
            
            return posts_pb2.CommentPostResponse(
                success=True,
                message="Comment added successfully",
                comment=self._format_comment_message(comment)
            )
            
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {str(e)}")
            return posts_pb2.CommentPostResponse()

    async def GetPostComments(self, request, context):
        try:
            post = await Post.get_or_none(id=request.post_id)
            if not post:
                await context.abort(StatusCode.NOT_FOUND, "Post not found")
                return posts_pb2.GetPostCommentsResponse()
            
            page = request.page or 1
            page_size = request.page_size or 10
            offset = (page - 1) * page_size
            
            comments_query = PostComment.filter(post_id=post.id)
            total_count = await comments_query.count()
            comments = await comments_query.offset(offset).limit(page_size).order_by("-created_at")
            
            comment_messages = [self._format_comment_message(c) for c in comments]
            
            return posts_pb2.GetPostCommentsResponse(
                comments=comment_messages,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {str(e)}")
            return posts_pb2.GetPostCommentsResponse()

    def _format_comment_message(self, comment: PostComment):
        created_at_ts = Timestamp()
        if comment.created_at:
            created_at_ts.FromDatetime(comment.created_at)
        
        updated_at_ts = Timestamp()
        if comment.updated_at:
            updated_at_ts.FromDatetime(comment.updated_at)
        
        return posts_pb2.PostComment(
            id=comment.id,
            post_id=str(comment.post_id),
            user_id=comment.user_id,
            content=comment.content,
            created_at=created_at_ts,
            updated_at=updated_at_ts
        ) 