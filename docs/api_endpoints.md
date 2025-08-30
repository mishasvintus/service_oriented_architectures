# API Endpoints Documentation

Документация всех доступных API эндпоинтов в системе социальной сети.

## REST API (через API Gateway)

Все REST API запросы проходят через API Gateway на порту `8000`.

### Аутентификация

#### POST /api/register
Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "login": "string",
  "email": "string", 
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "YYYY-MM-DD",
  "phone": "string"
}
```

#### POST /api/login
Аутентификация пользователя.

**Тело запроса:**
```json
{
  "login": "string",
  "password": "string"
}
```

**Ответ:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Пользователи

#### GET /api/users/me
Получение информации о текущем пользователе.

**Заголовки:** `Authorization: Bearer <token>`

#### PUT /api/users/me
Обновление профиля текущего пользователя.

**Заголовки:** `Authorization: Bearer <token>`

#### GET /api/users/{user_id}
Получение информации о пользователе по ID.

### Посты

#### POST /api/posts
Создание нового поста.

**Заголовки:** `Authorization: Bearer <token>`

**Тело запроса:**
```json
{
  "title": "string",
  "description": "string",
  "is_private": false,
  "tags": ["tag1", "tag2"]
}
```

#### GET /api/posts
Получение списка постов.

**Параметры запроса:**
- `limit` (int): Количество постов (по умолчанию 10)
- `offset` (int): Смещение (по умолчанию 0)

#### GET /api/posts/{post_id}
Получение поста по ID.

#### PUT /api/posts/{post_id}
Обновление поста.

**Заголовки:** `Authorization: Bearer <token>`

#### DELETE /api/posts/{post_id}
Удаление поста.

**Заголовки:** `Authorization: Bearer <token>`

#### POST /api/posts/{post_id}/view
Отметка просмотра поста.

**Заголовки:** `Authorization: Bearer <token>`

#### POST /api/posts/{post_id}/like
Лайк поста.

**Заголовки:** `Authorization: Bearer <token>`

#### DELETE /api/posts/{post_id}/like
Удаление лайка поста.

**Заголовки:** `Authorization: Bearer <token>`

#### POST /api/posts/{post_id}/comments
Добавление комментария к посту.

**Заголовки:** `Authorization: Bearer <token>`

**Тело запроса:**
```json
{
  "content": "string"
}
```

#### GET /api/posts/{post_id}/comments
Получение комментариев к посту.

### Статистика

#### GET /api/statistics/posts/{post_id}
Получение статистики поста.

**Ответ:**
```json
{
  "post_id": "string",
  "views_count": 0,
  "likes_count": 0,
  "comments_count": 0
}
```

#### GET /api/statistics/posts/{post_id}/dynamics
Получение динамики активности поста.

**Параметры запроса:**
- `days` (int): Количество дней для анализа (по умолчанию 7)

#### GET /api/statistics/top-posts
Получение топа постов.

**Параметры запроса:**
- `limit` (int): Количество постов (по умолчанию 10)

#### GET /api/statistics/top-users
Получение топа пользователей.

**Параметры запроса:**
- `limit` (int): Количество пользователей (по умолчанию 10)

## gRPC Services

### User Service (порт 50052)

**Proto файл:** `services/user_service/protos/users.proto`

#### Методы:
- `GetUser(GetUserRequest) -> UserResponse`
- `UpdateUser(UpdateUserRequest) -> UserResponse`
- `CreateUser(CreateUserRequest) -> UserResponse`

### Post Service (порт 50051)

**Proto файл:** `services/post_service/protos/posts.proto`

#### Методы:
- `CreatePost(CreatePostRequest) -> PostResponse`
- `GetPost(GetPostRequest) -> PostResponse`
- `UpdatePost(UpdatePostRequest) -> PostResponse`
- `DeletePost(DeletePostRequest) -> DeletePostResponse`
- `ListPosts(ListPostsRequest) -> ListPostsResponse`
- `ViewPost(ViewPostRequest) -> ViewPostResponse`
- `LikePost(LikePostRequest) -> LikePostResponse`
- `UnlikePost(UnlikePostRequest) -> UnlikePostResponse`
- `CommentPost(CommentPostRequest) -> CommentPostResponse`
- `GetPostComments(GetPostCommentsRequest) -> GetPostCommentsResponse`

### Statistics Service (порт 50053)

**Proto файл:** `services/statistics_service/protos/statistics.proto`

#### Методы:
- `GetPostStats(GetPostStatsRequest) -> GetPostStatsResponse`
- `GetPostViewsDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetPostLikesDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetPostCommentsDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetTopPosts(GetTopPostsRequest) -> GetTopPostsResponse`
- `GetTopUsers(GetTopUsersRequest) -> GetTopUsersResponse`

## Коды ошибок

### HTTP Status Codes

- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

### gRPC Status Codes

- `OK` - Успешный запрос
- `INVALID_ARGUMENT` - Неверные аргументы
- `NOT_FOUND` - Ресурс не найден
- `PERMISSION_DENIED` - Доступ запрещен
- `UNAUTHENTICATED` - Не авторизован
- `INTERNAL` - Внутренняя ошибка

## Примеры использования

### Создание поста с последующим получением статистики

```bash
# 1. Регистрация пользователя
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "date_of_birth": "1990-01-01",
    "phone": "+1234567890"
  }'

# 2. Аутентификация
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "password123"
  }'

# 3. Создание поста
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Мой первый пост",
    "description": "Описание поста",
    "is_private": false,
    "tags": ["тест", "первый пост"]
  }'

# 4. Получение статистики поста
curl -X GET http://localhost:8000/api/statistics/posts/<post_id> \
  -H "Authorization: Bearer <token>"
```

## Автоматическая документация

Для получения актуальной OpenAPI документации:

```bash
# Генерация документации
python3 scripts/generate_openapi.py

# Просмотр в браузере
open http://localhost:8000/docs  # Swagger UI
open http://localhost:8000/redoc # ReDoc
``` 