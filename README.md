Гончаров Михаил Алексеевич

БПМИ225

Социальная сеть

## Архитектура системы

Система состоит из нескольких микросервисов:

### Сервисы
- **API Gateway** (`api_service`) - REST API на порту 8000
- **User Service** (`user_service`) - Управление пользователями на порту 8001  
- **Post Service** (`post_service`) - gRPC сервис постов на порту 50051
- **Statistics Service** (`statistics_service`) - gRPC сервис аналитики на порту 50053
- **PostgreSQL** - База данных на порту 5432
- **ClickHouse** - Аналитическая база данных на порту 9000 (HTTP: 8123)
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

**Statistics API endpoints:**
- `GET /api/posts/{post_id}/stats` - Получить статистику поста (просмотры, лайки, комментарии)
- `GET /api/posts/{post_id}/dynamics/views` - Динамика просмотров поста за период
- `GET /api/posts/{post_id}/dynamics/likes` - Динамика лайков поста за период
- `GET /api/posts/{post_id}/dynamics/comments` - Динамика комментариев поста за период
- `GET /api/statistics/posts/top` - Топ постов по метрике (views/likes/comments)
- `GET /api/statistics/users/top` - Топ пользователей по метрике (views/likes/comments)

**Kafka события:**
- `user-registrations` - События регистрации пользователей
- `post-views` - События просмотров постов
- `post-likes` - События лайков/дизлайков постов
- `post-comments` - События комментариев к постам

### Statistics Service

Statistics Service обрабатывает события из Kafka и сохраняет аналитические данные в ClickHouse для быстрого получения статистики.

**Возможности:**
- 📊 Сбор и агрегация статистики по постам и пользователям
- 🔄 Обработка событий из Kafka в реальном времени
- 📈 Построение динамики метрик за период
- 🏆 Формирование топов по различным метрикам
- ⚡ Быстрые запросы благодаря ClickHouse

**Архитектура:**
- **gRPC API** - для получения статистики другими сервисами
- **Kafka Consumer** - для обработки событий в реальном времени
- **ClickHouse Client** - для работы с аналитической БД
- **REST API** - через API Gateway для внешних клиентов

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
scripts/run_tests.sh unit          # Unit тесты всех сервисов
scripts/run_tests.sh integration   # Интеграционные тесты всех сервисов
scripts/run_tests.sh kafka         # Kafka тесты
```

Подробная документация по тестированию: [`scripts/testing/TESTING.md`](scripts/testing/TESTING.md)

### Структура проекта

```
├── services/                # Микросервисы
│   ├── api_service/         # API Gateway (FastAPI)
│   ├── user_service/        # User Service (FastAPI + gRPC)
│   ├── post_service/        # Post Service (gRPC)
│   └── statistics_service/  # Statistics Service (gRPC + ClickHouse + Kafka)
├── tests/                   # End-to-End тесты
├── scripts/                 # Вспомогательные скрипты
│   ├── database/            # Скрипты БД
│   ├── clickhouse/          # Скрипты ClickHouse
│   └── testing/             # Тестовые скрипты
├── docs/                    # Документация
└── docker-compose.yml       # Конфигурация Docker
```