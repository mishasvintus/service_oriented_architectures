#!/usr/bin/env python3
"""
Ручной тест для Statistics Service
Этот файл предназначен для быстрой проверки работоспособности gRPC API
"""
import grpc
import sys
import os

# Добавляем путь к protobuf файлам
sys.path.insert(0, os.path.dirname(__file__))

from statistics_service.protos import statistics_pb2, statistics_pb2_grpc

def test_statistics_service():
    """Тестирование Statistics Service"""
    
    # Подключение к gRPC сервису
    channel = grpc.insecure_channel('localhost:50053')
    stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
    
    print("🧪 Тестирование Statistics Service...")
    
    try:
        # Тест 1: GetPostStats
        print("\n1️⃣ Тест GetPostStats:")
        request = statistics_pb2.GetPostStatsRequest(post_id="test-post-123")
        response = stub.GetPostStats(request, timeout=10)
        print(f"   ✅ Post ID: {response.post_id}")
        print(f"   📊 Views: {response.views_count}")
        print(f"   👍 Likes: {response.likes_count}")
        print(f"   💬 Comments: {response.comments_count}")
        
        # Тест 2: GetPostViewsDynamics
        print("\n2️⃣ Тест GetPostViewsDynamics:")
        request = statistics_pb2.GetPostDynamicsRequest(post_id="test-post-123", days=7)
        response = stub.GetPostViewsDynamics(request, timeout=10)
        print(f"   ✅ Post ID: {response.post_id}")
        print(f"   📈 Metric: {response.metric}")
        print(f"   📊 Data points: {len(response.dynamics)}")
        
        # Тест 3: GetTopPosts
        print("\n3️⃣ Тест GetTopPosts:")
        request = statistics_pb2.GetTopPostsRequest(metric="views", limit=5)
        response = stub.GetTopPosts(request, timeout=10)
        print(f"   ✅ Metric: {response.metric}")
        print(f"   🏆 Top posts: {len(response.posts)}")
        for i, post in enumerate(response.posts[:3]):
            print(f"      {i+1}. Post {post.post_id}: {post.count} views")
        
        # Тест 4: GetTopUsers
        print("\n4️⃣ Тест GetTopUsers:")
        request = statistics_pb2.GetTopUsersRequest(metric="likes", limit=5)
        response = stub.GetTopUsers(request, timeout=10)
        print(f"   ✅ Metric: {response.metric}")
        print(f"   👥 Top users: {len(response.users)}")
        for i, user in enumerate(response.users[:3]):
            print(f"      {i+1}. User {user.user_id}: {user.count} likes")
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e.code()} - {e.details()}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        channel.close()
    
    return True

if __name__ == "__main__":
    success = test_statistics_service()
    sys.exit(0 if success else 1) 