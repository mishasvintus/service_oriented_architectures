import grpc
import os
from dotenv import load_dotenv
from .protos import posts_pb2_grpc, statistics_pb2_grpc

load_dotenv()

POST_SERVICE_GRPC_URL = os.getenv("POST_SERVICE_GRPC_URL", "post_service:50051")
STATISTICS_SERVICE_GRPC_URL = os.getenv("STATISTICS_SERVICE_GRPC_URL", "statistics_service:50053")

def get_posts_stub():
    channel = grpc.insecure_channel(POST_SERVICE_GRPC_URL)
    return posts_pb2_grpc.PostServiceStub(channel)

def get_statistics_stub():
    channel = grpc.insecure_channel(STATISTICS_SERVICE_GRPC_URL)
    return statistics_pb2_grpc.StatisticsServiceStub(channel) 