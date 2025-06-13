from fastapi import APIRouter, Depends, HTTPException, status
from api_service.app.schemas.post_schema import (
    PostCreate, PostOut, PostUpdate, PaginatedPostOut,
    ViewPostResponse, LikePostResponse, CommentCreate, CommentResponse, PaginatedCommentsOut
)
from api_service.app.grpc_client import get_posts_stub
from api_service.protos import posts_pb2, posts_pb2_grpc
import grpc
from google.protobuf.json_format import MessageToDict
from api_service.app.auth import get_current_user_id

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.post("", response_model=PostOut, status_code=status.HTTP_200_OK)
def create_post(
    post_data: PostCreate, 
    stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), 
    user_id: int = Depends(get_current_user_id)
):
    try:
        request = posts_pb2.CreatePostRequest(
            title=post_data.title,
            description=post_data.description,
            author_id=user_id,
            is_private=post_data.is_private,
            tags=post_data.tags
        )
        response = stub.CreatePost(request)
        return MessageToDict(response.post, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=e.details())

@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: str, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.GetPostRequest(id=post_id, requester_id=user_id)
        response = stub.GetPost(request)
        return MessageToDict(response.post, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=status_code, detail=e.details())

@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: str, post_data: PostUpdate, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        update_data = post_data.model_dump(exclude_unset=True)
        request = posts_pb2.UpdatePostRequest(id=post_id, requester_id=user_id, **update_data)
        response = stub.UpdatePost(request)
        return MessageToDict(response.post, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=status_code, detail=e.details())

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.DeletePostRequest(id=post_id, requester_id=user_id)
        stub.DeletePost(request)
        return
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=status_code, detail=e.details())

@router.get("", response_model=PaginatedPostOut)
def list_posts(page: int = 1, page_size: int = 10, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub)):
    try:
        request = posts_pb2.ListPostsRequest(page=page, page_size=page_size)
        response = stub.ListPosts(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.details())

@router.post("/{post_id}/view", response_model=ViewPostResponse)
def view_post(post_id: str, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.ViewPostRequest(post_id=post_id, user_id=user_id)
        response = stub.ViewPost(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            status_code = status.HTTP_403_FORBIDDEN
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            status_code = status.HTTP_404_NOT_FOUND  # Treat invalid UUID as not found
        raise HTTPException(status_code=status_code, detail=e.details())

@router.post("/{post_id}/like", response_model=LikePostResponse)
def like_post(post_id: str, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.LikePostRequest(post_id=post_id, user_id=user_id)
        response = stub.LikePost(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=e.details())

@router.delete("/{post_id}/like", response_model=LikePostResponse)
def unlike_post(post_id: str, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.UnlikePostRequest(post_id=post_id, user_id=user_id)
        response = stub.UnlikePost(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=e.details())

@router.post("/{post_id}/comments", response_model=CommentResponse)
def comment_post(post_id: str, comment_data: CommentCreate, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub), user_id: int = Depends(get_current_user_id)):
    try:
        request = posts_pb2.CommentPostRequest(
            post_id=post_id, 
            user_id=user_id, 
            content=comment_data.content
        )
        response = stub.CommentPost(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=e.details())

@router.get("/{post_id}/comments", response_model=PaginatedCommentsOut)
def get_post_comments(post_id: str, page: int = 1, page_size: int = 10, stub: posts_pb2_grpc.PostServiceStub = Depends(get_posts_stub)):
    try:
        request = posts_pb2.GetPostCommentsRequest(post_id=post_id, page=page, page_size=page_size)
        response = stub.GetPostComments(request)
        return MessageToDict(response, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except grpc.RpcError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if e.code() == grpc.StatusCode.NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=e.details()) 