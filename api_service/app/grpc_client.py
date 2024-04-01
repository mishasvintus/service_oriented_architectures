import grpc
import os
from dotenv import load_dotenv
from api_service.protos import posts_pb2_grpc

load_dotenv()

POST_SERVICE_GRPC_URL = os.getenv("POST_SERVICE_GRPC_URL", "post_service:50051")

def get_posts_stub():
    channel = grpc.insecure_channel(POST_SERVICE_GRPC_URL)
    return posts_pb2_grpc.PostServiceStub(channel) 