import asyncio
import logging
import grpc
from tortoise import Tortoise
from post_service.app.config import DATABASE_URL
from post_service.protos import posts_pb2_grpc
from post_service.app.servicer import PostService

async def init_db():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["post_service.app.models"]}
    )
    await Tortoise.generate_schemas()

async def grpc_server():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    
    server = grpc.aio.server()
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    
    server.add_insecure_port('[::]:50051')
    logging.info("Starting gRPC server on port 50051")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(grpc_server()) 