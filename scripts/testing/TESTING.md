# 🧪 Тестирование микросервисной архитектуры

Этот документ описывает как запускать тесты для проверки функциональности системы.

## 📋 Типы тестов

### 1. Unit тесты
- Тестируют отдельные компоненты и функции
- Не требуют запущенных сервисов
- Используют моки для внешних зависимостей

### 2. Интеграционные тесты
- Тестируют взаимодействие между сервисами
- Требуют запущенные сервисы
- Проверяют REST API и gRPC взаимодействия

### 3. Kafka тесты
- Тестируют событийную архитектуру
- Проверяют отправку и получение событий
- Требуют запущенный Kafka

### 4. End-to-End тесты
- Полные сценарии от начала до конца
- Тестируют весь поток: Регистрация → Посты → Kafka → Statistics → API
- Требуют все запущенные сервисы

## 🚀 Запуск тестов

### Предварительные требования

1. **Установите зависимости для тестов:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Запустите сервисы:**
   ```bash
   docker-compose up -d
   ```

3. **Убедитесь что все сервисы работают:**
   ```bash
   docker-compose ps
   ```

### Команды для запуска

#### Все тесты сразу
```bash
scripts/run_tests.sh
# или
scripts/run_tests.sh all
# или
python3 scripts/testing/run_tests.py
```

#### Только unit тесты
```bash
scripts/run_tests.sh unit
# или
python3 scripts/testing/test_unit.py
```

#### Только интеграционные тесты
```bash
scripts/run_tests.sh integration
# или
python3 scripts/testing/test_integration.py
```

#### Только Kafka тесты
```bash
scripts/run_tests.sh kafka
# или
python3 -m pytest tests/test_kafka_integration.py -v
```

#### Только End-to-End тесты
```bash
scripts/run_tests.sh e2e
# или
python3 scripts/testing/run_tests.py e2e
# или
python3 -m pytest tests/test_full_e2e_flow.py -v
```

## 📁 Структура тестов

```
├── scripts/testing/                     # 🔧 Тестовые скрипты
│   ├── run_tests.py                     # Главный скрипт запуска тестов
│   ├── test_unit.py                     # Запуск всех unit тестов
│   ├── test_integration.py              # Запуск всех интеграционных тестов
│   └── test_kafka.py                    # Запуск Kafka тестов
│
├── services/
│   ├── user_service/
│   │   ├── unit_tests/                      # 🧪 Unit тесты
│   │   │   ├── test_kafka_producer.py       # Kafka producer (мок)
│   │   │   ├── test_servicer.py             # gRPC сервис
│   │   │   └── ...
│   │   └── integrational_tests/             # 🔗 Интеграционные тесты
│   │       └── test_integration.py          # gRPC интеграция
│   │
│   ├── post_service/
│   │   ├── unit_tests/                      # 🧪 Unit тесты
│   │   │   ├── test_kafka_producer.py       # Kafka producer (мок)
│   │   │   ├── test_servicer.py             # gRPC сервис
│   │   │   ├── test_new_methods.py          # Новые методы
│   │   │   └── ...
│   │   └── integrational_tests/             # 🔗 Интеграционные тесты
│   │       └── test_integration.py          # gRPC интеграция
│   │
│   ├── api_service/
│   │   ├── unit_tests/                      # 🧪 Unit тесты
│   │   │   └── test_posts_router.py         # FastAPI роутеры (мок)
│   │   └── integrational_tests/             # 🔗 Интеграционные тесты
│   │       └── test_integration.py          # REST API интеграция
│   │
│   └── statistics_service/
│   ├── unit_tests/                      # 🧪 Unit тесты
│   │   ├── test_clickhouse_client.py    # ClickHouse клиент (мок)
│   │   ├── test_kafka_consumer.py       # Kafka consumer (мок)
│   │   └── test_servicer.py             # gRPC сервис (мок)
│   └── integrational_tests/             # 🔗 Интеграционные тесты
│       └── test_integration.py          # gRPC + REST API интеграция
│
├── tests/                               # 🌐 End-to-End тесты
│   ├── test_kafka_integration.py        # Kafka события (реальные)
│   └── test_full_e2e_flow.py            # Полный E2E тест социальной сети
│
├── run_tests.sh                         # 🚀 Удобный запуск из корня
└── TESTING.md                           # 📖 Эта документация
```

### Типы тестов по уровням:

1. **Unit тесты** (мокают внешние зависимости):
   - `**/unit_tests/test_kafka_producer.py` - тестируют логику Kafka producer'ов
   - `**/unit_tests/test_servicer.py` - тестируют gRPC сервисы
   - `**/unit_tests/test_posts_router.py` - тестируют FastAPI роутеры

2. **Интеграционные тесты** (используют реальные сервисы):
   - `**/integrational_tests/test_integration.py` - тестируют gRPC/REST взаимодействие
   
3. **End-to-End тесты** (полный поток):
   - `tests/test_kafka_integration.py` - тестируют реальные Kafka события

## 🔧 Что тестируется

### User Service
- ✅ Регистрация и аутентификация пользователей
- ✅ JWT токены
- ✅ Отправка событий регистрации в Kafka
- ✅ Валидация данных

### Post Service
- ✅ CRUD операции с постами
- ✅ Новые функции: просмотр, лайки, комментарии
- ✅ Контроль доступа к приватным постам
- ✅ Отправка событий в Kafka
- ✅ Пагинация комментариев

### API Gateway
- ✅ Проксирование запросов к микросервисам
- ✅ Новые REST endpoints
- ✅ Statistics API endpoints
- ✅ Обработка ошибок
- ✅ Авторизация

### Statistics Service
- ✅ ClickHouse интеграция для аналитики
- ✅ Kafka consumer для обработки событий
- ✅ gRPC API для получения статистики
- ✅ REST API через API Gateway
- ✅ Агрегация данных по постам и пользователям

### Kafka Events
- ✅ События регистрации пользователей
- ✅ События просмотра постов
- ✅ События лайков/дизлайков
- ✅ События комментариев
- ✅ Корректность структуры событий

## 📊 Покрытие тестами

### Новые функции (из newtask.md)
- ✅ POST `/api/posts/{post_id}/view` - просмотр поста
- ✅ POST `/api/posts/{post_id}/like` - лайк поста  
- ✅ DELETE `/api/posts/{post_id}/like` - убрать лайк
- ✅ POST `/api/posts/{post_id}/comments` - добавить комментарий
- ✅ GET `/api/posts/{post_id}/comments` - получить комментарии с пагинацией

### Statistics API endpoints
- ✅ GET `/api/posts/{post_id}/stats` - статистика поста
- ✅ GET `/api/posts/{post_id}/dynamics/views` - динамика просмотров
- ✅ GET `/api/posts/{post_id}/dynamics/likes` - динамика лайков
- ✅ GET `/api/posts/{post_id}/dynamics/comments` - динамика комментариев
- ✅ GET `/api/statistics/posts/top` - топ постов по метрике
- ✅ GET `/api/statistics/users/top` - топ пользователей по метрике

### Kafka топики
- ✅ `user-registrations` - регистрации пользователей
- ✅ `post-views` - просмотры постов
- ✅ `post-likes` - лайки постов
- ✅ `post-comments` - комментарии к постам

## 🐛 Отладка тестов

### Если тесты падают:

1. **Проверьте статус сервисов:**
   ```bash
   docker-compose ps
   docker-compose logs
   ```

2. **Проверьте доступность endpoints:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/docs
   curl http://localhost:8080
   ```

3. **Проверьте Kafka топики:**
   - Откройте Kafka UI: http://localhost:8080
   - Убедитесь что все 4 топика созданы

4. **Запустите тесты с подробным выводом:**
   ```bash
   scripts/run_tests.sh unit
   # или для конкретного типа тестов:
   python3 -m pytest services/user_service/unit_tests/ -v
   python3 -m pytest tests/test_kafka_integration.py -v -s
   ```

### Частые проблемы:

- **Сервисы не запущены** → `docker-compose up -d`
- **Kafka недоступен** → Перезапустите композ: `docker-compose down -v && docker-compose up -d`
- **Порты заняты** → Проверьте что нет других процессов на портах 8000, 8001, 5432, 9092, 8080
- **Зависимости не установлены** → `pip install -r requirements-test.txt`

## 📈 Результаты

После запуска тестов вы увидите:
- ✅ Количество пройденных тестов
- ❌ Детали провалившихся тестов  
- 📊 Общую сводку по всем типам тестов

Все тесты должны проходить для подтверждения корректной работы системы согласно требованиям из `newtask.md`. 