# 🚀 Демонстрация API социальной сети - Curl команды

Этот файл содержит последовательность curl команд для демонстрации работы всех сервисов микросервисной социальной сети.

## Предварительные требования

1. Запустите все сервисы: `docker-compose up -d`
2. Убедитесь что все сервисы доступны:
   - API Gateway: http://localhost:8000
   - Kafka UI: http://localhost:8080
   - Swagger: http://localhost:8000/docs

## ⚠️ Важно: Аутентификация

**Система использует двухэтапную аутентификацию:**
1. **Регистрация** (`/api/register`) - создает пользователя, НО НЕ возвращает токен
2. **Логин** (`/api/login`) - возвращает JWT токен для авторизации

**Для получения токена обязательно выполните оба шага!**

## Автоматический запуск

Для автоматического выполнения всех команд:
```bash
./demo_api_flow.sh
```

## Ручное выполнение команд

### 1. 👥 Регистрация и аутентификация пользователей (User Service)

#### Регистрация Alice
```bash
curl -X POST 'http://localhost:8000/api/register' \
-H 'Content-Type: application/json' \
-d '{
    "login": "alice_demo",
    "email": "alice@example.com",
    "password": "password123",
    "first_name": "Alice",
    "last_name": "Johnson"
}'
```

#### Логин Alice для получения токена
```bash
curl -X POST 'http://localhost:8000/api/login' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'username=alice_demo&password=password123'
```

**Пример ответа:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Регистрация Bob
```bash
curl -X POST 'http://localhost:8000/api/register' \
-H 'Content-Type: application/json' \
-d '{
    "login": "bob_demo",
    "email": "bob@example.com",
    "password": "password456",
    "first_name": "Bob",
    "last_name": "Smith"
}'
```

#### Логин Bob для получения токена
```bash
curl -X POST 'http://localhost:8000/api/login' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'username=bob_demo&password=password456'
```

#### Регистрация Charlie
```bash
curl -X POST 'http://localhost:8000/api/register' \
-H 'Content-Type: application/json' \
-d '{
    "login": "charlie_demo",
    "email": "charlie@example.com",
    "password": "password789",
    "first_name": "Charlie",
    "last_name": "Brown"
}'
```

#### Логин Charlie для получения токена
```bash
curl -X POST 'http://localhost:8000/api/login' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'username=charlie_demo&password=password789'
```

**⚠️ Сохраните токены из ответов логина для дальнейшего использования!**

### 2. 📝 Создание постов (Post Service)

#### Alice создает пост о путешествии
```bash
curl -X POST 'http://localhost:8000/api/posts' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{
    "title": "Мое путешествие в Японию",
    "description": "Невероятные впечатления от поездки в Токио! Рекомендую всем посетить храм Сенсо-дзи.",
    "is_public": true
}'
```

#### Bob создает пост о технологиях
```bash
curl -X POST 'http://localhost:8000/api/posts' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN' \
-H 'Content-Type: application/json' \
-d '{
    "title": "Микросервисы vs Монолит",
    "description": "Размышления о том, когда стоит использовать микросервисную архитектуру, а когда лучше остаться с монолитом.",
    "is_public": true
}'
```

#### Charlie создает пост о кулинарии
```bash
curl -X POST 'http://localhost:8000/api/posts' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{
    "title": "Рецепт идеальной пасты",
    "description": "Секреты приготовления настоящей итальянской пасты карбонара. Главное - не добавлять сливки!",
    "is_public": true
}'
```

**⚠️ Сохраните ID постов из ответов для дальнейшего использования!**

### 3. 👀 Просмотр постов (генерация событий в Kafka)

#### Bob просматривает пост Alice
```bash
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/view' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'
```

#### Charlie просматривает пост Alice
```bash
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/view' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN'
```

#### Alice просматривает пост Bob
```bash
curl -X POST 'http://localhost:8000/api/posts/BOB_POST_ID/view' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'
```

#### Charlie просматривает пост Bob
```bash
curl -X POST 'http://localhost:8000/api/posts/BOB_POST_ID/view' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN'
```

#### Alice просматривает пост Charlie
```bash
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/view' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'
```

#### Bob просматривает пост Charlie
```bash
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/view' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'
```

### 4. ❤️ Лайки постов (генерация событий в Kafka)

#### Лайки для поста Alice
```bash
# Bob лайкает пост Alice
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/like' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'

# Charlie лайкает пост Alice
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/like' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN'
```

#### Лайки для поста Bob
```bash
# Alice лайкает пост Bob
curl -X POST 'http://localhost:8000/api/posts/BOB_POST_ID/like' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'
```

#### Лайки для поста Charlie
```bash
# Alice лайкает пост Charlie
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/like' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'

# Bob лайкает пост Charlie
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/like' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'
```

### 5. 💬 Комментарии к постам (генерация событий в Kafka)

#### Комментарии к посту Alice
```bash
# Bob комментирует пост Alice
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "Потрясающие фотографии! Я тоже мечтаю побывать в Японии."}'

# Charlie комментирует пост Alice
curl -X POST 'http://localhost:8000/api/posts/ALICE_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "А какие еще места в Токио ты посетила?"}'
```

#### Комментарии к посту Bob
```bash
# Alice комментирует пост Bob
curl -X POST 'http://localhost:8000/api/posts/BOB_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "Отличная статья! Согласна, что микросервисы не всегда нужны."}'

# Charlie комментирует пост Bob
curl -X POST 'http://localhost:8000/api/posts/BOB_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "А как ты относишься к serverless архитектуре?"}'
```

#### Комментарии к посту Charlie
```bash
# Alice комментирует пост Charlie
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "Спасибо за рецепт! Обязательно попробую приготовить."}'

# Bob комментирует пост Charlie
curl -X POST 'http://localhost:8000/api/posts/CHARLIE_POST_ID/comments' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN' \
-H 'Content-Type: application/json' \
-d '{"content": "А какой сыр лучше использовать для карбонары?"}'
```

### 6. 📖 Получение комментариев

#### Получение комментариев к постам
```bash
# Комментарии к посту Alice
curl -X GET 'http://localhost:8000/api/posts/ALICE_POST_ID/comments?page=1&page_size=10'

# Комментарии к посту Bob
curl -X GET 'http://localhost:8000/api/posts/BOB_POST_ID/comments?page=1&page_size=10'

# Комментарии к посту Charlie
curl -X GET 'http://localhost:8000/api/posts/CHARLIE_POST_ID/comments?page=1&page_size=10'
```

### 7. ⏳ Ожидание обработки событий

**Подождите 5-10 секунд для обработки событий Statistics Service через Kafka**

### 8. 📊 Статистика постов (Statistics Service)

#### Получение базовой статистики
```bash
# Статистика поста Alice
curl -X GET 'http://localhost:8000/api/posts/ALICE_POST_ID/stats' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'

# Статистика поста Bob
curl -X GET 'http://localhost:8000/api/posts/BOB_POST_ID/stats' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'

# Статистика поста Charlie
curl -X GET 'http://localhost:8000/api/posts/CHARLIE_POST_ID/stats' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN'
```

### 9. 📈 Динамика метрик за период

#### Динамика за последний час
```bash
# Получите текущее время в UTC (для macOS)
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START_TIME=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ")

# Для Linux используйте:
# START_TIME=$(date -u -d '1 hour ago' +"%Y-%m-%dT%H:%M:%SZ")

# Динамика просмотров поста Alice
curl -X GET "http://localhost:8000/api/posts/ALICE_POST_ID/dynamics/views?start_time=$START_TIME&end_time=$END_TIME" \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'

# Динамика лайков поста Alice
curl -X GET "http://localhost:8000/api/posts/ALICE_POST_ID/dynamics/likes?start_time=$START_TIME&end_time=$END_TIME" \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'

# Динамика комментариев поста Alice
curl -X GET "http://localhost:8000/api/posts/ALICE_POST_ID/dynamics/comments?start_time=$START_TIME&end_time=$END_TIME" \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'
```

### 10. 🏆 Топ постов и пользователей (Statistics Service)

#### Топ постов
```bash
# Топ 10 постов по просмотрам
curl -X GET 'http://localhost:8000/api/statistics/posts/top?metric=views&limit=10'

# Топ 10 постов по лайкам
curl -X GET 'http://localhost:8000/api/statistics/posts/top?metric=likes&limit=10'

# Топ 10 постов по комментариям
curl -X GET 'http://localhost:8000/api/statistics/posts/top?metric=comments&limit=10'
```

#### Топ пользователей
```bash
# Топ 10 пользователей по просмотрам
curl -X GET 'http://localhost:8000/api/statistics/users/top?metric=views&limit=10'

# Топ 10 пользователей по лайкам
curl -X GET 'http://localhost:8000/api/statistics/users/top?metric=likes&limit=10'

# Топ 10 пользователей по комментариям
curl -X GET 'http://localhost:8000/api/statistics/users/top?metric=comments&limit=10'
```

### 11. 👤 Получение профилей пользователей

```bash
# Профиль Alice
curl -X GET 'http://localhost:8000/api/profile' \
-H 'Authorization: Bearer YOUR_ALICE_TOKEN'

# Профиль Bob
curl -X GET 'http://localhost:8000/api/profile' \
-H 'Authorization: Bearer YOUR_BOB_TOKEN'

# Профиль Charlie
curl -X GET 'http://localhost:8000/api/profile' \
-H 'Authorization: Bearer YOUR_CHARLIE_TOKEN'
```

### 12. 📋 Получение списка постов

```bash
# Список всех публичных постов
curl -X GET 'http://localhost:8000/api/posts?page=1&page_size=10'
```

## 🔍 Мониторинг событий

### Kafka UI
Откройте http://localhost:8080 для просмотра событий в топиках:
- `user-registrations` - события регистрации
- `post-views` - события просмотров
- `post-likes` - события лайков
- `post-comments` - события комментариев

### Swagger документация
Откройте http://localhost:8000/docs для интерактивной документации API

## 🎯 Что демонстрируется

1. **User Service**: Регистрация пользователей, JWT аутентификация
2. **Post Service**: CRUD операции с постами, взаимодействия (просмотры, лайки, комментарии)
3. **API Gateway**: Маршрутизация запросов, авторизация
4. **Kafka**: Асинхронная обработка событий
5. **Statistics Service**: Агрегация статистики, аналитика
6. **ClickHouse**: Быстрые аналитические запросы

## 🚀 Архитектурные особенности

- **Микросервисная архитектура**: Каждый сервис независим
- **Событийно-ориентированная архитектура**: Kafka для асинхронной обработки
- **gRPC**: Быстрое межсервисное взаимодействие
- **REST API**: Удобный интерфейс для клиентов
- **Аналитика в реальном времени**: ClickHouse + Statistics Service 