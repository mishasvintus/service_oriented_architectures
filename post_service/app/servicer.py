from post_service.protos import posts_pb2, posts_pb2_grpc
from post_service.app.models import Post
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import StatusCode
import grpc

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