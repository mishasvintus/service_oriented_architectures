import unittest
import requests
import grpc
import time
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к модулям statistics_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from statistics_service.protos import statistics_pb2, statistics_pb2_grpc


class TestStatisticsServiceIntegration(unittest.TestCase):
    """Интеграционные тесты для Statistics Service"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка для всех тестов"""
        cls.api_gateway_url = "http://localhost:8000"
        cls.statistics_grpc_url = "localhost:50053"
        
        # Проверяем доступность сервисов
        cls._wait_for_services()
    
    @classmethod
    def _wait_for_services(cls, timeout=30):
        """Ожидание готовности сервисов"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Проверяем API Gateway
                response = requests.get(f"{cls.api_gateway_url}/docs", timeout=5)
                if response.status_code == 200:
                    print("✅ API Gateway доступен")
                    break
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        else:
            raise Exception("API Gateway недоступен")
        
        # Проверяем gRPC сервис
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                channel = grpc.insecure_channel(cls.statistics_grpc_url)
                stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
                
                # Пробуем простой запрос
                request = statistics_pb2.GetPostStatsRequest(post_id="test")
                response = stub.GetPostStats(request, timeout=5)
                print("✅ Statistics gRPC сервис доступен")
                channel.close()
                break
            except grpc.RpcError:
                pass
            except Exception:
                pass
            
            time.sleep(1)
        else:
            raise Exception("Statistics gRPC сервис недоступен")
    
    def test_grpc_get_post_stats(self):
        """Тест gRPC метода получения статистики поста"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
        
        try:
            request = statistics_pb2.GetPostStatsRequest(post_id="test-post-123")
            response = stub.GetPostStats(request, timeout=10)
            
            # Проверяем структуру ответа
            self.assertEqual(response.post_id, "test-post-123")
            self.assertIsInstance(response.views_count, int)
            self.assertIsInstance(response.likes_count, int)
            self.assertIsInstance(response.comments_count, int)
            self.assertGreaterEqual(response.views_count, 0)
            self.assertGreaterEqual(response.likes_count, 0)
            self.assertGreaterEqual(response.comments_count, 0)
            
        finally:
            channel.close()
    
    def test_grpc_get_post_views_dynamics(self):
        """Тест gRPC метода получения динамики просмотров"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
        
        try:
            # Запрос за последние 7 дней
            request = statistics_pb2.GetPostDynamicsRequest(
                post_id="test-post-123",
                days=7
            )
            response = stub.GetPostViewsDynamics(request, timeout=10)
            
            # Проверяем структуру ответа
            self.assertEqual(response.post_id, "test-post-123")
            self.assertTrue(hasattr(response, 'dynamics'))
            
            # Если есть данные, проверяем их структуру
            for point in response.dynamics:
                self.assertIsInstance(point.date, str)
                self.assertIsInstance(point.count, int)
                self.assertGreaterEqual(point.count, 0)
                
        finally:
            channel.close()
    
    def test_grpc_get_top_posts(self):
        """Тест gRPC метода получения топ постов"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
        
        try:
            request = statistics_pb2.GetTopPostsRequest(
                metric="views",
                limit=5
            )
            response = stub.GetTopPosts(request, timeout=10)
            
            # Проверяем структуру ответа
            self.assertTrue(hasattr(response, 'posts'))
            self.assertLessEqual(len(response.posts), 5)
            
            # Если есть данные, проверяем их структуру и сортировку
            prev_count = float('inf')
            for post in response.posts:
                self.assertIsInstance(post.post_id, str)
                self.assertIsInstance(post.count, int)
                self.assertGreaterEqual(post.count, 0)
                self.assertLessEqual(post.count, prev_count)  # Проверяем сортировку по убыванию
                prev_count = post.count
                
        finally:
            channel.close()
    
    def test_grpc_get_top_users(self):
        """Тест gRPC метода получения топ пользователей"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
        
        try:
            request = statistics_pb2.GetTopUsersRequest(
                metric="posts",
                limit=5
            )
            response = stub.GetTopUsers(request, timeout=10)
            
            # Проверяем структуру ответа
            self.assertTrue(hasattr(response, 'users'))
            self.assertLessEqual(len(response.users), 5)
            
            # Если есть данные, проверяем их структуру
            for user in response.users:
                self.assertIsInstance(user.user_id, str)
                self.assertIsInstance(user.count, int)
                self.assertGreaterEqual(user.count, 0)
                
        finally:
            channel.close()
    
    def test_grpc_error_handling(self):
        """Тест обработки ошибок в gRPC"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
        
        try:
            # Тест с невалидными параметрами
            request = statistics_pb2.GetPostDynamicsRequest(
                post_id="test-post-123",
                days=-1  # Невалидное количество дней
            )
            
            # Не должно вызывать исключений
            response = stub.GetPostViewsDynamics(request, timeout=10)
            self.assertTrue(hasattr(response, 'dynamics'))
            
        finally:
            channel.close()
    
    def test_grpc_service_availability(self):
        """Тест доступности gRPC сервиса"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        
        try:
            # Проверяем что канал может подключиться
            grpc.channel_ready_future(channel).result(timeout=10)
            
            # Проверяем что сервис отвечает
            stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
            request = statistics_pb2.GetPostStatsRequest(post_id="health-check")
            response = stub.GetPostStats(request, timeout=5)
            
            # Ответ должен быть получен без ошибок
            self.assertIsNotNone(response)
            
        finally:
            channel.close()


class TestStatisticsAPIIntegration(unittest.TestCase):
    """Интеграционные тесты для Statistics REST API через API Gateway"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка для всех тестов"""
        cls.api_gateway_url = "http://localhost:8000"
        cls.auth_token = None
        
        # Получаем токен аутентификации для тестов
        cls._get_auth_token()
    
    @classmethod
    def _get_auth_token(cls):
        """Получение токена аутентификации"""
        try:
            # Пытаемся зарегистрировать тестового пользователя
            register_data = {
                "login": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpass123"
            }
            
            response = requests.post(
                f"{cls.api_gateway_url}/api/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code == 201:
                # Логинимся
                login_data = {
                    "username": register_data["login"],
                    "password": register_data["password"]
                }
                
                response = requests.post(
                    f"{cls.api_gateway_url}/api/login",
                    data=login_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    cls.auth_token = response.json().get("access_token")
                    print("✅ Получен токен аутентификации для тестов")
                    return
            
            print("⚠️ Не удалось получить токен аутентификации, тесты API будут пропущены")
            
        except Exception as e:
            print(f"⚠️ Ошибка при получении токена: {e}")
    
    def setUp(self):
        """Настройка для каждого теста"""
        if not self.auth_token:
            self.skipTest("Нет токена аутентификации")
        
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_api_get_post_stats(self):
        """Тест REST API получения статистики поста"""
        response = requests.get(
            f"{self.api_gateway_url}/api/posts/test-post-123/stats",
            headers=self.headers,
            timeout=10
        )
        
        # API должен отвечать (даже если данных нет)
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("post_id", data)
            self.assertIn("views_count", data)
            self.assertIn("likes_count", data)
            self.assertIn("comments_count", data)
    
    def test_api_get_top_posts(self):
        """Тест REST API получения топ постов"""
        response = requests.get(
            f"{self.api_gateway_url}/api/statistics/posts/top?metric=views&limit=5",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("posts", data)
        self.assertIsInstance(data["posts"], list)
        self.assertLessEqual(len(data["posts"]), 5)
    
    def test_api_get_top_users(self):
        """Тест REST API получения топ пользователей"""
        response = requests.get(
            f"{self.api_gateway_url}/api/statistics/users/top?metric=views&limit=5",
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
        self.assertIsInstance(data["users"], list)
        self.assertLessEqual(len(data["users"]), 5)


if __name__ == '__main__':
    unittest.main() 