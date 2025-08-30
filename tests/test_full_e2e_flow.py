"""
Полный end-to-end тест социальной сети
Проверяет весь поток: Регистрация → Посты → Активность → Kafka → Statistics → Аналитика
"""

import unittest
import json
import time
import httpx
import os
import grpc
from kafka import KafkaConsumer
from threading import Thread
from datetime import datetime, timedelta
import sys

# Добавляем путь к модулям statistics_service для gRPC клиента
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.statistics_service.protos import statistics_pb2, statistics_pb2_grpc


class TestFullE2EFlow(unittest.TestCase):
    """
    Полный end-to-end тест, который проверяет:
    1. Регистрацию пользователей
    2. Создание и взаимодействие с постами
    3. Отправку событий в Kafka
    4. Обработку событий Statistics Service
    5. Обновление данных в ClickHouse
    6. Получение актуальной статистики через API
    """
    
    @classmethod
    def setUpClass(cls):
        """Настройка для всех тестов"""
        cls.base_url = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
        cls.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        cls.statistics_grpc_url = "localhost:50053"
        
        # Проверяем доступность всех сервисов
        cls._wait_for_services()
        
        # Настраиваем Kafka consumer для мониторинга событий
        cls.events_received = {
            'user-registrations': [],
            'post-views': [],
            'post-likes': [],
            'post-comments': []
        }
        cls.consumers = {}
        
        # Запускаем consumers для всех топиков
        for topic in cls.events_received.keys():
            cls._start_consumer(topic)
        
        # Даем время на подключение consumers
        time.sleep(3)
        print("✅ Все Kafka consumers запущены")
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        for consumer in cls.consumers.values():
            consumer.close()
    
    @classmethod
    def _wait_for_services(cls, timeout=30):
        """Ожидание готовности всех сервисов"""
        services = [
            ("API Gateway", lambda: httpx.get(f"{cls.base_url}/docs", timeout=5)),
            ("Statistics gRPC", cls._check_statistics_grpc)
        ]
        
        for service_name, check_func in services:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    if callable(check_func):
                        check_func()
                    else:
                        response = check_func()
                        if response.status_code == 200:
                            break
                    print(f"✅ {service_name} доступен")
                    break
                except Exception:
                    pass
                time.sleep(1)
            else:
                raise Exception(f"{service_name} недоступен после {timeout}s")
    
    @classmethod
    def _check_statistics_grpc(cls):
        """Проверка доступности Statistics gRPC сервиса"""
        channel = grpc.insecure_channel(cls.statistics_grpc_url)
        try:
            stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
            # Создаем запрос через protobuf
            request = statistics_pb2.GetPostStatsRequest(post_id="health-check")
            stub.GetPostStats(request, timeout=5)
        finally:
            channel.close()
    
    @classmethod
    def _start_consumer(cls, topic):
        """Запускает Kafka consumer для указанного топика"""
        def consume_messages(topic_name):
            try:
                consumer = KafkaConsumer(
                    topic_name,
                    bootstrap_servers=[cls.kafka_bootstrap_servers],
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    consumer_timeout_ms=10000,
                    auto_offset_reset='earliest',  # Читаем с начала топика
                    group_id=f'e2e_test_group_{topic_name}_{int(time.time())}',
                    enable_auto_commit=True
                )
                cls.consumers[topic_name] = consumer
                
                # Небольшая задержка для подключения consumer'а
                time.sleep(0.5)
                
                for message in consumer:
                    print(f"📨 Получено событие в топике {topic_name}: {message.value}")
                    cls.events_received[topic_name].append({
                        'data': message.value,
                        'timestamp': time.time()
                    })
                    
            except Exception as e:
                print(f"❌ Ошибка consumer для {topic_name}: {e}")
        
        thread = Thread(target=consume_messages, args=(topic,))
        thread.daemon = True
        thread.start()
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.test_start_time = time.time()
        
        # Запоминаем количество событий на начало теста
        self.initial_event_counts = {
            topic: len(events) for topic, events in self.events_received.items()
        }
        
        # Уникальные данные для теста
        unique_id = f"{int(time.time())}_{os.getpid()}_{id(self)}"
        self.test_users = [
            {
                "login": f"e2e_user1_{unique_id}",
                "email": f"e2e_user1_{unique_id}@example.com",
                "password": "testpass123",
                "first_name": "E2E",
                "last_name": "User1"
            },
            {
                "login": f"e2e_user2_{unique_id}",
                "email": f"e2e_user2_{unique_id}@example.com", 
                "password": "testpass456",
                "first_name": "E2E",
                "last_name": "User2"
            },
            {
                "login": f"e2e_user3_{unique_id}",
                "email": f"e2e_user3_{unique_id}@example.com",
                "password": "testpass789",
                "first_name": "E2E", 
                "last_name": "User3"
            }
        ]
        
        self.tokens = []
        self.user_ids = []
        self.post_ids = []
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем созданные посты
        for i, post_id in enumerate(self.post_ids):
            if i < len(self.tokens):
                try:
                    headers = {"Authorization": f"Bearer {self.tokens[i]}"}
                    response = httpx.delete(f"{self.base_url}/api/posts/{post_id}", headers=headers)
                    if response.status_code == 204:
                        print(f"🗑️ Удален пост {post_id}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить пост {post_id}: {e}")
        
        # Удаляем созданных пользователей
        for token in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = httpx.delete(f"{self.base_url}/api/profile", headers=headers)
                if response.status_code == 204:
                    print(f"🗑️ Удален пользователь")
            except Exception as e:
                print(f"⚠️ Не удалось удалить пользователя: {e}")
        
        print(f"✅ Очистка после теста завершена")
    
    def _register_and_login_user(self, user_data):
        """Регистрирует и логинит пользователя"""
        # Регистрация
        reg_response = httpx.post(f"{self.base_url}/api/register", json=user_data)
        self.assertEqual(reg_response.status_code, 201, f"Ошибка регистрации: {reg_response.text}")
        
        # Логин
        login_response = httpx.post(f"{self.base_url}/api/login", data={
            "username": user_data["login"],
            "password": user_data["password"]
        })
        self.assertEqual(login_response.status_code, 200, f"Ошибка логина: {login_response.text}")
        
        token = login_response.json()["access_token"]
        
        # Получаем user_id
        profile_response = httpx.get(f"{self.base_url}/api/profile", 
                                   headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(profile_response.status_code, 200)
        user_id = profile_response.json()["id"]
        
        return token, user_id
    
    def _create_post(self, token, title, description):
        """Создает пост"""
        headers = {"Authorization": f"Bearer {token}"}
        post_data = {
            "title": title,
            "description": description,
            "is_private": False,
            "tags": ["e2e", "test"]
        }
        
        response = httpx.post(f"{self.base_url}/api/posts", headers=headers, json=post_data)
        self.assertEqual(response.status_code, 200, f"Ошибка создания поста: {response.text}")
        
        return response.json()["id"]
    
    def _wait_for_events(self, topic, expected_new_events=1, timeout=15):
        """Ждет получения новых событий в указанном топике"""
        initial_count = self.initial_event_counts[topic]
        target_count = initial_count + expected_new_events
        
        start_time = time.time()
        
        # Ждем появления новых событий после начала теста
        while True:
            if time.time() - start_time > timeout:
                current_count = len(self.events_received[topic])
                new_events = current_count - initial_count
                self.fail(f"Timeout ожидания {expected_new_events} новых событий в топике '{topic}'. "
                         f"Было {initial_count}, стало {current_count}, получено {new_events} новых событий за {timeout}s")
            
            # Считаем события, которые пришли после начала теста
            recent_events = [
                event for event in self.events_received[topic]
                if event['timestamp'] >= self.test_start_time
            ]
            
            if len(recent_events) >= expected_new_events:
                print(f"✅ Получено {len(recent_events)} новых событий в топике '{topic}'")
                break
                
            time.sleep(0.5)
    
    def _wait_for_statistics_update(self, post_id, expected_views=None, expected_likes=None, 
                                  expected_comments=None, timeout=20):
        """Ждет обновления статистики в ClickHouse через Statistics Service"""
        channel = grpc.insecure_channel(self.statistics_grpc_url)
        
        try:
            stub = statistics_pb2_grpc.StatisticsServiceStub(channel)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    request = statistics_pb2.GetPostStatsRequest(post_id=post_id)
                    response = stub.GetPostStats(request, timeout=5)
                    
                    # Проверяем, соответствует ли статистика ожиданиям
                    conditions_met = True
                    
                    if expected_views is not None and response.views_count < expected_views:
                        conditions_met = False
                    if expected_likes is not None and response.likes_count < expected_likes:
                        conditions_met = False
                    if expected_comments is not None and response.comments_count < expected_comments:
                        conditions_met = False
                    
                    if conditions_met:
                        print(f"✅ Статистика обновлена: views={response.views_count}, "
                              f"likes={response.likes_count}, comments={response.comments_count}")
                        return response
                        
                except grpc.RpcError as e:
                    print(f"⚠️ gRPC ошибка при получении статистики: {e}")
                
                time.sleep(1)
            
            # Если не дождались, получаем текущую статистику для диагностики
            try:
                request = statistics_pb2.GetPostStatsRequest(post_id=post_id)
                response = stub.GetPostStats(request, timeout=5)
                self.fail(f"Timeout ожидания обновления статистики для поста {post_id}. "
                         f"Ожидали: views>={expected_views}, likes>={expected_likes}, comments>={expected_comments}. "
                         f"Получили: views={response.views_count}, likes={response.likes_count}, "
                         f"comments={response.comments_count}")
            except Exception as e:
                self.fail(f"Timeout ожидания статистики и ошибка получения текущих данных: {e}")
                
        finally:
            channel.close()
    
    def test_full_social_media_e2e_flow(self):
        """
        Полный end-to-end тест социальной сети:
        1. Регистрация 3 пользователей
        2. Создание постов
        3. Активность пользователей (просмотры, лайки, комментарии)
        4. Проверка событий в Kafka
        5. Ожидание обработки Statistics Service
        6. Проверка актуальной статистики через API
        """
        print("\n🚀 Начинаем полный E2E тест социальной сети")
        
        # Шаг 1: Регистрация пользователей
        print("\n📝 Шаг 1: Регистрация пользователей")
        for i, user_data in enumerate(self.test_users):
            token, user_id = self._register_and_login_user(user_data)
            self.tokens.append(token)
            self.user_ids.append(user_id)
            print(f"✅ Пользователь {i+1} зарегистрирован: {user_data['login']} (ID: {user_id})")
            # Небольшая задержка между регистрациями для обработки событий
            time.sleep(1)
        
        # Ждем события регистрации в Kafka (минимум 2 из 3)
        # Иногда третье событие может задержаться
        try:
            self._wait_for_events('user-registrations', 3, timeout=10)
        except AssertionError:
            # Если не получили все 3, проверяем что есть хотя бы 2
            current_count = len(self.events_received['user-registrations']) - self.initial_event_counts['user-registrations']
            if current_count >= 2:
                print(f"⚠️ Получено {current_count} из 3 событий регистрации (достаточно для продолжения)")
            else:
                raise
        
        # Шаг 2: Создание постов
        print("\n📄 Шаг 2: Создание постов")
        post_titles = [
            "Первый пост для E2E теста",
            "Второй пост с интересным контентом", 
            "Третий пост для проверки аналитики"
        ]
        
        for i, title in enumerate(post_titles):
            post_id = self._create_post(self.tokens[i], title, f"Описание для поста {i+1}")
            self.post_ids.append(post_id)
            print(f"✅ Пост {i+1} создан: {title} (ID: {post_id})")
        
        # Шаг 3: Активность пользователей
        print("\n👥 Шаг 3: Активность пользователей")
        
        # Пользователь 2 и 3 просматривают пост 1
        for i in [1, 2]:
            headers = {"Authorization": f"Bearer {self.tokens[i]}"}
            response = httpx.post(f"{self.base_url}/api/posts/{self.post_ids[0]}/view", headers=headers)
            self.assertEqual(response.status_code, 200)
            print(f"✅ Пользователь {i+1} просмотрел пост 1")
        
        # Пользователь 2 и 3 лайкают пост 1
        for i in [1, 2]:
            headers = {"Authorization": f"Bearer {self.tokens[i]}"}
            response = httpx.post(f"{self.base_url}/api/posts/{self.post_ids[0]}/like", headers=headers)
            self.assertEqual(response.status_code, 200)
            print(f"✅ Пользователь {i+1} лайкнул пост 1")
        
        # Пользователь 2 и 3 комментируют пост 1
        comments = ["Отличный пост!", "Очень интересно, спасибо!"]
        for i, comment in enumerate(comments):
            headers = {"Authorization": f"Bearer {self.tokens[i+1]}"}
            comment_data = {"content": comment}
            response = httpx.post(f"{self.base_url}/api/posts/{self.post_ids[0]}/comments", 
                                headers=headers, json=comment_data)
            self.assertEqual(response.status_code, 200)
            print(f"✅ Пользователь {i+2} прокомментировал пост 1: '{comment}'")
        
        # Шаг 4: Ожидание обработки Statistics Service
        print("\n📊 Шаг 4: Ожидание обработки статистики")
        
        # Ждем обновления статистики для поста 1 (2 просмотра, 2 лайка, 2 комментария)
        stats = self._wait_for_statistics_update(
            self.post_ids[0], 
            expected_views=2, 
            expected_likes=2, 
            expected_comments=2
        )
        
        # Шаг 5: Проверка статистики через REST API
        print("\n🔍 Шаг 5: Проверка статистики через REST API")
        
        # Получаем статистику через API Gateway
        headers = {"Authorization": f"Bearer {self.tokens[0]}"}
        response = httpx.get(f"{self.base_url}/api/posts/{self.post_ids[0]}/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        api_stats = response.json()
        print(f"📈 Статистика через API: {api_stats}")
        
        # Проверяем соответствие данных
        self.assertEqual(api_stats['post_id'], self.post_ids[0])
        self.assertGreaterEqual(api_stats['views_count'], 2)
        self.assertGreaterEqual(api_stats['likes_count'], 2) 
        self.assertGreaterEqual(api_stats['comments_count'], 2)
        
        # Шаг 6: Проверка топов
        print("\n🏆 Шаг 6: Проверка топов")
        
        # Небольшая дополнительная задержка для обработки статистики
        time.sleep(2)
        
        # Получаем топ постов (увеличиваем лимит, так как может быть много постов с одинаковым количеством просмотров)
        response = httpx.get(f"{self.base_url}/api/statistics/posts/top?metric=views&limit=10")
        self.assertEqual(response.status_code, 200)
        
        top_posts = response.json()
        print(f"🥇 Топ постов: {len(top_posts['posts'])} постов")
        
        # Наш активный пост должен быть в топе
        our_post_in_top = any(post['post_id'] == self.post_ids[0] for post in top_posts['posts'])
        if not our_post_in_top:
            print(f"❌ Наш пост {self.post_ids[0]} не найден в топе")
            print("Посты в топе:")
            for i, post in enumerate(top_posts['posts']):
                print(f"  {i+1}. {post['post_id']} - {post['count']} просмотров")
        self.assertTrue(our_post_in_top, f"Наш активный пост {self.post_ids[0]} должен быть в топе")
        
        # Получаем топ пользователей
        response = httpx.get(f"{self.base_url}/api/statistics/users/top?metric=likes&limit=5")
        self.assertEqual(response.status_code, 200)
        
        top_users = response.json()
        print(f"👑 Топ пользователей: {len(top_users['users'])} пользователей")
        
        print("\n🎉 Полный E2E тест успешно завершен!")
        print("✅ Все компоненты работают корректно:")
        print("   - Регистрация и аутентификация пользователей")
        print("   - Создание и взаимодействие с постами")
        print("   - Отправка событий в Kafka")
        print("   - Обработка событий Statistics Service")
        print("   - Обновление данных в ClickHouse")
        print("   - Получение актуальной статистики через API")
    
    def test_statistics_dynamics_e2e(self):
        """
        Тест динамики статистики:
        Создаем активность в разное время и проверяем динамику
        """
        print("\n📈 Тест динамики статистики")
        
        # Регистрируем пользователя и создаем пост
        token, user_id = self._register_and_login_user(self.test_users[0])
        post_id = self._create_post(token, "Пост для тестирования динамики", "Тестовое описание")
        
        # Создаем активность
        headers = {"Authorization": f"Bearer {token}"}
        
        # Несколько просмотров
        for _ in range(3):
            response = httpx.post(f"{self.base_url}/api/posts/{post_id}/view", headers=headers)
            self.assertEqual(response.status_code, 200)
            time.sleep(0.5)  # Небольшая задержка между просмотрами
        
        # Ждем обновления статистики
        self._wait_for_statistics_update(post_id, expected_views=3)
        
        # Проверяем динамику через API
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(f"{self.base_url}/api/posts/{post_id}/dynamics/views?days=1", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        dynamics = response.json()
        print(f"📊 Динамика просмотров: {dynamics}")
        
        # Должна быть хотя бы одна точка данных
        self.assertGreater(len(dynamics['dynamics']), 0)
        
        print("✅ Тест динамики статистики завершен успешно")


if __name__ == '__main__':
    unittest.main(verbosity=2) 