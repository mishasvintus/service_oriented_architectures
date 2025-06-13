Гончаров Михаил Алексеевич

БПМИ225

Социальная сеть

## Архитектура системы

Система состоит из нескольких микросервисов:

### Сервисы
- **API Gateway** (`api_service`) - REST API на порту 8000
- **User Service** (`user_service`) - Управление пользователями на порту 8001  
- **Post Service** (`post_service`) - gRPC сервис постов на порту 50051
- **PostgreSQL** - База данных на порту 5432
- **Kafka** - Message broker на порту 9092
- **Kafka UI** - Web интерфейс для Kafka на порту 8080

### Новый функционал
Реализованы следующие возможности согласно техническому заданию:

**REST API endpoints:**
- `POST /api/posts/{post_id}/view` - Просмотр поста с отправкой события в Kafka
- `POST /api/posts/{post_id}/like` - Лайк поста с отправкой события в Kafka
- `DELETE /api/posts/{post_id}/like` - Убрать лайк поста  
- `POST /api/posts/{post_id}/comments` - Добавить комментарий с отправкой события в Kafka
- `GET /api/posts/{post_id}/comments` - Получить комментарии с пагинацией

**Kafka события:**
- `user-registrations` - События регистрации пользователей
- `post-views` - События просмотров постов
- `post-likes` - События лайков/дизлайков постов
- `post-comments` - События комментариев к постам

### Запуск системы

```bash
docker-compose up -d
```

После запуска доступны:
- API Gateway: http://localhost:8000
- Kafka UI: http://localhost:8080
- Swagger документация: http://localhost:8000/docs

### Тестирование

```bash
# Запуск всех тестов
scripts/run_tests.sh

# Запуск конкретного типа тестов
scripts/run_tests.sh unit          # Unit тесты
scripts/run_tests.sh integration   # Интеграционные тесты  
scripts/run_tests.sh kafka         # Kafka тесты
```

Подробная документация по тестированию: [`scripts/testing/TESTING.md`](scripts/testing/TESTING.md)

### Структура проекта

```
├── api_service/             # API Gateway (FastAPI)
├── user_service/            # User Service (FastAPI + gRPC)
├── post_service/            # Post Service (gRPC)
├── tests/                   # End-to-End тесты
├── scripts/                 # Вспомогательные скрипты
│   ├── database/            # Скрипты БД
│   └── testing/             # Тестовые скрипты
├── docs/                    # Документация
└── docker-compose.yml       # Конфигурация Docker
```