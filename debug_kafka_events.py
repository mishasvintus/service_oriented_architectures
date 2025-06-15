#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с Kafka событиями
"""

import json
import time
import httpx
import os
from kafka import KafkaConsumer
from threading import Thread
import uuid

BASE_URL = "http://localhost:8000"

def create_kafka_consumer(topic):
    """Создает Kafka consumer для указанного топика"""
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000,
        auto_offset_reset='earliest',
        group_id=f'debug_group_{topic}_{int(time.time())}',
        enable_auto_commit=True
    )
    return consumer

def monitor_events(topic, events_list, duration=30):
    """Мониторит события в указанном топике"""
    consumer = create_kafka_consumer(topic)
    start_time = time.time()
    
    print(f"🔍 Начинаем мониторинг топика '{topic}' на {duration} секунд...")
    
    try:
        for message in consumer:
            elapsed = time.time() - start_time
            if elapsed > duration:
                break
                
            event_data = {
                'data': message.value,
                'timestamp': time.time(),
                'partition': message.partition,
                'offset': message.offset
            }
            events_list.append(event_data)
            print(f"📨 [{elapsed:.1f}s] Получено событие в '{topic}': {message.value}")
            
    except Exception as e:
        print(f"❌ Ошибка мониторинга топика '{topic}': {e}")
    finally:
        consumer.close()

def test_user_registrations():
    """Тестирует регистрацию пользователей и события"""
    print("\n🧪 Тест регистрации пользователей")
    print("=" * 50)
    
    # Запускаем мониторинг событий
    events = []
    monitor_thread = Thread(target=monitor_events, args=('user-registrations', events, 20))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Даем время на подключение consumer
    time.sleep(2)
    
    # Регистрируем 3 пользователей
    users = []
    for i in range(3):
        unique_id = f"{int(time.time())}_{i}_{uuid.uuid4().hex[:8]}"
        user_data = {
            "login": f"debug_user_{unique_id}",
            "email": f"debug_{unique_id}@example.com",
            "password": "testpass123",
            "first_name": "Debug",
            "last_name": f"User{i+1}"
        }
        
        print(f"\n📝 Регистрируем пользователя {i+1}: {user_data['login']}")
        
        try:
            response = httpx.post(f"{BASE_URL}/api/register", json=user_data, timeout=10)
            if response.status_code == 201:
                user_info = response.json()
                users.append(user_info)
                print(f"✅ Пользователь {i+1} зарегистрирован: ID={user_info['id']}")
            else:
                print(f"❌ Ошибка регистрации пользователя {i+1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Исключение при регистрации пользователя {i+1}: {e}")
        
        # Небольшая задержка между регистрациями
        time.sleep(1)
    
    # Ждем завершения мониторинга
    print(f"\n⏳ Ждем события в течение 15 секунд...")
    monitor_thread.join(timeout=15)
    
    # Анализируем результаты
    print(f"\n📊 Результаты:")
    print(f"Зарегистрировано пользователей: {len(users)}")
    print(f"Получено событий в Kafka: {len(events)}")
    
    if len(events) != len(users):
        print(f"❌ ПРОБЛЕМА: Ожидали {len(users)} событий, получили {len(events)}")
        
        # Показываем детали
        print("\n🔍 Детали зарегистрированных пользователей:")
        for i, user in enumerate(users):
            print(f"  {i+1}. ID={user['id']}, login={user['login']}")
        
        print("\n🔍 Детали полученных событий:")
        for i, event in enumerate(events):
            data = event['data']
            print(f"  {i+1}. user_id={data.get('user_id')}, timestamp={data.get('timestamp')}")
        
        # Проверяем, какие user_id отсутствуют
        registered_ids = {user['id'] for user in users}
        event_ids = {event['data']['user_id'] for event in events}
        missing_ids = registered_ids - event_ids
        
        if missing_ids:
            print(f"\n❌ Отсутствуют события для user_id: {missing_ids}")
    else:
        print("✅ Все события получены корректно!")
    
    return len(users), len(events)

def test_post_views():
    """Тестирует просмотры постов и события"""
    print("\n🧪 Тест просмотров постов")
    print("=" * 50)
    
    # Сначала регистрируем пользователя и создаем пост
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    user_data = {
        "login": f"post_test_user_{unique_id}",
        "email": f"post_test_{unique_id}@example.com",
        "password": "testpass123"
    }
    
    # Регистрация
    reg_response = httpx.post(f"{BASE_URL}/api/register", json=user_data)
    if reg_response.status_code != 201:
        print(f"❌ Не удалось зарегистрировать пользователя: {reg_response.text}")
        return 0, 0
    
    # Логин
    login_response = httpx.post(f"{BASE_URL}/api/login", data={
        "username": user_data["login"],
        "password": user_data["password"]
    })
    if login_response.status_code != 200:
        print(f"❌ Не удалось войти: {login_response.text}")
        return 0, 0
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем пост
    post_data = {
        "title": "Тестовый пост для диагностики",
        "description": "Этот пост используется для тестирования событий просмотра",
        "is_private": False,
        "tags": ["debug", "test"]
    }
    
    post_response = httpx.post(f"{BASE_URL}/api/posts", headers=headers, json=post_data)
    if post_response.status_code != 200:
        print(f"❌ Не удалось создать пост: {post_response.text}")
        return 0, 0
    
    post_id = post_response.json()["id"]
    print(f"✅ Создан пост: {post_id}")
    
    # Запускаем мониторинг событий просмотра
    events = []
    monitor_thread = Thread(target=monitor_events, args=('post-views', events, 15))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    time.sleep(2)
    
    # Делаем несколько просмотров
    view_count = 3
    for i in range(view_count):
        print(f"\n👁️ Просмотр {i+1} поста {post_id}")
        
        try:
            view_response = httpx.post(f"{BASE_URL}/api/posts/{post_id}/view", headers=headers)
            if view_response.status_code == 200:
                print(f"✅ Просмотр {i+1} выполнен")
            else:
                print(f"❌ Ошибка просмотра {i+1}: {view_response.status_code} - {view_response.text}")
        except Exception as e:
            print(f"❌ Исключение при просмотре {i+1}: {e}")
        
        time.sleep(1)
    
    # Ждем события
    print(f"\n⏳ Ждем события просмотра...")
    monitor_thread.join(timeout=10)
    
    # Анализируем результаты
    print(f"\n📊 Результаты просмотров:")
    print(f"Выполнено просмотров: {view_count}")
    print(f"Получено событий в Kafka: {len(events)}")
    
    if len(events) != view_count:
        print(f"❌ ПРОБЛЕМА: Ожидали {view_count} событий, получили {len(events)}")
    else:
        print("✅ Все события просмотра получены корректно!")
    
    return view_count, len(events)

def main():
    """Главная функция диагностики"""
    print("🔧 Диагностика Kafka событий")
    print("=" * 60)
    
    # Проверяем доступность сервисов
    try:
        response = httpx.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ API Gateway недоступен")
            return
        print("✅ API Gateway доступен")
    except Exception as e:
        print(f"❌ Не удалось подключиться к API Gateway: {e}")
        return
    
    # Тестируем регистрации
    reg_expected, reg_actual = test_user_registrations()
    
    # Тестируем просмотры постов
    view_expected, view_actual = test_post_views()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    print(f"Регистрации: {reg_actual}/{reg_expected} событий получено")
    print(f"Просмотры: {view_actual}/{view_expected} событий получено")
    
    total_expected = reg_expected + view_expected
    total_actual = reg_actual + view_actual
    
    if total_actual == total_expected:
        print("🎉 ВСЕ СОБЫТИЯ ПОЛУЧЕНЫ КОРРЕКТНО!")
    else:
        print(f"❌ ПРОБЛЕМА: Потеряно {total_expected - total_actual} событий из {total_expected}")
        print("\n🔍 Возможные причины:")
        print("1. Kafka producer отправляет события асинхронно")
        print("2. Проблемы с сетью между сервисами и Kafka")
        print("3. Kafka consumer подключается слишком поздно")
        print("4. Проблемы с конфигурацией Kafka")

if __name__ == "__main__":
    main() 