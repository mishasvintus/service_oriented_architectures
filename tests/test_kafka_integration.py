import unittest
import json
import time
import httpx
import os
from kafka import KafkaConsumer
from threading import Thread
import pytest


class TestKafkaIntegration(unittest.TestCase):
    """Интеграционные тесты для проверки Kafka событий"""
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
        cls.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        cls.events_received = {
            'user-registrations': [],
            'post-views': [],
            'post-likes': [],
            'post-comments': []
        }
        cls.consumers = {}
        cls.consumer_threads = {}
        
        for topic in cls.events_received.keys():
            cls._start_consumer(topic)
        
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        for consumer in cls.consumers.values():
            consumer.close()
    
    @classmethod
    def _start_consumer(cls, topic):
        """Запускает Kafka consumer для указанного топика"""
        def consume_messages(topic_name):
            try:
                consumer = KafkaConsumer(
                    topic_name,
                    bootstrap_servers=[cls.kafka_bootstrap_servers],
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    consumer_timeout_ms=5000,
                    auto_offset_reset='earliest',
                    group_id=f'test_group_{topic_name}_{int(time.time())}_{os.getpid()}',
                    enable_auto_commit=False
                )
                cls.consumers[topic_name] = consumer
                print(f"Started consumer for topic {topic_name}")
                
                for message in consumer:
                    print(f"Received message in topic {topic_name}: {message.value}")
                    cls.events_received[topic_name].append(message.value)
                    
            except Exception as e:
                print(f"Consumer error for {topic_name}: {e}")
        
        thread = Thread(target=consume_messages, args=(topic,))
        thread.daemon = True
        thread.start()
        cls.consumer_threads[topic] = thread
    
    def setUp(self):
        self.test_start_time = time.time()
        
        self.initial_event_counts = {
            topic: len(events) for topic, events in self.events_received.items()
        }
        
        unique_id = f"{int(time.time())}_{os.getpid()}_{id(self)}"
        self.test_user = {
            "login": f"kafka_test_{unique_id}",
            "email": f"kafka_test_{unique_id}@example.com",
            "password": "testpass123"
        }
        self.token = None
        self.post_id = None
        self.user_id = None
    
    def _register_and_login_user(self):
        """Регистрирует и логинит пользователя, возвращает токен"""
        # Регистрация
        reg_response = httpx.post(f"{self.base_url}/api/register", json=self.test_user)
        self.assertEqual(reg_response.status_code, 201)
        
        # Логин
        login_response = httpx.post(f"{self.base_url}/api/login", data={
            "username": self.test_user["login"],
            "password": self.test_user["password"]
        })
        self.assertEqual(login_response.status_code, 200)
        
        self.token = login_response.json()["access_token"]
        
        # Получаем user_id из токена или из ответа регистрации
        user_response = httpx.get(f"{self.base_url}/api/profile", 
                                 headers={"Authorization": f"Bearer {self.token}"})
        if user_response.status_code == 200:
            self.user_id = user_response.json()["id"]
        
        return self.token
    
    def _create_test_post(self):
        """Создает тестовый пост"""
        headers = {"Authorization": f"Bearer {self.token}"}
        post_data = {
            "title": "Kafka Test Post",
            "description": "Post for testing Kafka events",
            "is_private": False,
            "tags": ["kafka", "test"]
        }
        
        response = httpx.post(f"{self.base_url}/api/posts", headers=headers, json=post_data)
        self.assertEqual(response.status_code, 200)
        
        self.post_id = response.json()["id"]
        return self.post_id
    
    def _wait_for_events(self, topic, expected_count=1, timeout=5):
        """Ждет получения событий в указанном топике и проверяет результат"""
        initial_count = self.initial_event_counts[topic]
        start_time = time.time()
        while len(self.events_received[topic]) < initial_count + expected_count:
            if time.time() - start_time > timeout:
                current_count = len(self.events_received[topic])
                new_events = current_count - initial_count
                self.fail(f"Timeout waiting for {expected_count} new events in topic '{topic}'. "
                         f"Had {initial_count} events at start, now have {current_count} events, "
                         f"received {new_events} new events after {timeout}s")
            time.sleep(0.1)
    
    def _find_test_events(self, topic, event_type=None, post_id=None):
        """Находит события, связанные с текущим тестом"""
        test_events = []
        for event in self.events_received[topic]:
            # Фильтруем по типу события
            if event_type and event.get('event_type') != event_type:
                continue
            
            # Проверяем, относится ли событие к нашему тесту
            is_our_event = False
            
            # Если указан post_id, проверяем по нему
            if post_id and event.get('post_id') == post_id:
                is_our_event = True
            # Если это событие пользователя и user_id совпадает
            elif self.user_id and 'user_id' in event and event['user_id'] == self.user_id:
                is_our_event = True
                
            if is_our_event:
                test_events.append(event)
                
        return test_events
    
    def test_user_registration_event(self):
        """Тест отправки события регистрации пользователя"""
        self._register_and_login_user()
        
        self._wait_for_events('user-registrations', 1, 10)
        
        event = self.events_received['user-registrations'][-1]  # Получаем последнее событие
        self.assertEqual(event['event_type'], 'user_registration')
        self.assertIn('user_id', event)
        self.assertIn('registration_date', event)
        self.assertIn('timestamp', event)
    
    def test_post_view_event(self):
        """Тест отправки события просмотра поста"""
        self._register_and_login_user()
        self._create_test_post()
        
        # Просмотр поста
        headers = {"Authorization": f"Bearer {self.token}"}
        response = httpx.post(f"{self.base_url}/api/posts/{self.post_id}/view", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Ждем событие просмотра
        self._wait_for_events('post-views', 1)
        
        event = self.events_received['post-views'][-1]  # Получаем последнее событие
        self.assertEqual(event['event_type'], 'post_view')
        self.assertEqual(event['post_id'], self.post_id)
        self.assertIn('user_id', event)
        self.assertIn('timestamp', event)
    
    def test_post_like_events(self):
        """Тест отправки событий лайка и убирания лайка"""
        self._register_and_login_user()
        self._create_test_post()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Лайк поста
        like_response = httpx.post(f"{self.base_url}/api/posts/{self.post_id}/like", headers=headers)
        self.assertEqual(like_response.status_code, 200)
        
        # Ждем событие лайка
        self._wait_for_events('post-likes', 1)
        
        like_event = self.events_received['post-likes'][-1]  # Последнее событие (лайк)
        self.assertEqual(like_event['event_type'], 'post_like')
        self.assertEqual(like_event['post_id'], self.post_id)
        self.assertEqual(like_event['action'], 'like')
        self.assertIn('user_id', like_event)
        self.assertIn('timestamp', like_event)
        
        # Убираем лайк
        unlike_response = httpx.delete(f"{self.base_url}/api/posts/{self.post_id}/like", headers=headers)
        self.assertEqual(unlike_response.status_code, 200)
        
        # Ждем событие убирания лайка (еще одно событие)
        self._wait_for_events('post-likes', 1)
        
        unlike_event = self.events_received['post-likes'][-1]  # Последнее событие (unlike)
        self.assertEqual(unlike_event['event_type'], 'post_like')
        self.assertEqual(unlike_event['post_id'], self.post_id)
        self.assertEqual(unlike_event['action'], 'unlike')
        self.assertIn('user_id', unlike_event)
        self.assertIn('timestamp', unlike_event)
    
    def test_post_comment_event(self):
        """Тест отправки события комментария"""
        # Подготовка
        self._register_and_login_user()
        self._create_test_post()
        
        # Добавляем комментарий
        headers = {"Authorization": f"Bearer {self.token}"}
        comment_data = {"content": "This is a test comment for Kafka!"}
        
        response = httpx.post(f"{self.base_url}/api/posts/{self.post_id}/comments", 
                             headers=headers, json=comment_data)
        self.assertEqual(response.status_code, 200)
        
        comment_id = response.json()["comment"]["id"]
        
        # Ждем событие комментария
        self._wait_for_events('post-comments', 1)
        
        event = self.events_received['post-comments'][-1]  # Получаем последнее событие
        self.assertEqual(event['event_type'], 'post_comment')
        self.assertEqual(event['post_id'], self.post_id)
        self.assertEqual(event['comment_id'], comment_id)
        self.assertEqual(event['content'], "This is a test comment for Kafka!")
        self.assertIn('user_id', event)
        self.assertIn('timestamp', event)
    
    def test_multiple_events_flow(self):
        """Тест полного потока событий: регистрация -> пост -> просмотр -> лайк -> комментарий"""
        # 1. Регистрация пользователя
        self._register_and_login_user()
        self._wait_for_events('user-registrations', 1)
        
        # 2. Создание поста (событие не отправляется, но пост нужен для дальнейших тестов)
        self._create_test_post()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 3. Просмотр поста
        httpx.post(f"{self.base_url}/api/posts/{self.post_id}/view", headers=headers)
        self._wait_for_events('post-views', 1)
        
        # 4. Лайк поста
        httpx.post(f"{self.base_url}/api/posts/{self.post_id}/like", headers=headers)
        self._wait_for_events('post-likes', 1)
        
        # 5. Комментарий к посту
        comment_data = {"content": "Full flow test comment"}
        httpx.post(f"{self.base_url}/api/posts/{self.post_id}/comments", 
                  headers=headers, json=comment_data)
        self._wait_for_events('post-comments', 1)
        
        # Даем дополнительное время для получения события комментария
        time.sleep(1)
        
        # События уже проверены в _wait_for_events, переходим к проверке содержимого
        
        # Находим события нашего теста
        reg_events = self._find_test_events('user-registrations', 'user_registration')
        view_events = self._find_test_events('post-views', 'post_view', self.post_id)
        like_events = self._find_test_events('post-likes', 'post_like', self.post_id)
        comment_events = self._find_test_events('post-comments', 'post_comment', self.post_id)
        
        # Проверяем, что события найдены
        self.assertGreater(len(reg_events), 0, "Не найдено событие регистрации")
        self.assertGreater(len(view_events), 0, "Не найдено событие просмотра")
        self.assertGreater(len(like_events), 0, "Не найдено событие лайка")
        self.assertGreater(len(comment_events), 0, "Не найдено событие комментария")
        
        # Берем последние события
        reg_event = reg_events[-1]
        view_event = view_events[-1]
        like_event = like_events[-1]
        comment_event = comment_events[-1]
        
        # Все события должны содержать корректные данные
        self.assertEqual(reg_event['event_type'], 'user_registration')
        self.assertEqual(view_event['event_type'], 'post_view')
        self.assertEqual(like_event['event_type'], 'post_like')
        self.assertEqual(comment_event['event_type'], 'post_comment')
        
        # События поста должны ссылаться на один и тот же пост
        self.assertEqual(view_event['post_id'], self.post_id)
        self.assertEqual(like_event['post_id'], self.post_id)
        self.assertEqual(comment_event['post_id'], self.post_id)


if __name__ == '__main__':
    try:
        consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'])
        consumer.close()
        unittest.main()
    except Exception as e:
        print(f"Kafka недоступен, пропускаем тесты: {e}")
        exit(0) 