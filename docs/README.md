# Документация проекта

Эта директория содержит всю техническую документацию социальной сети.

## Содержание

### Архитектура
- [`architecture.md`](architecture.md) - Подробное описание архитектуры системы
- [`social_media.c4`](social_media.c4) - C4 диаграмма архитектуры

### База данных
- [`er.puml`](er.puml) - ER диаграмма базы данных

### API Документация
- [`api_endpoints.md`](api_endpoints.md) - Полное описание всех API эндпоинтов
- [`openapi/`](openapi/) - Директория с OpenAPI и gRPC документацией
  - [`openapi_combined.yaml`](openapi/openapi_combined.yaml) - Объединенная OpenAPI спецификация
  - [`api_gateway_openapi.yaml`](openapi/api_gateway_openapi.yaml) - OpenAPI для API Gateway
  - [`user_service_openapi.yaml`](openapi/user_service_openapi.yaml) - OpenAPI для User Service
  - [`grpc_services.md`](openapi/grpc_services.md) - Документация gRPC сервисов

### Тестирование
- [`../scripts/testing/TESTING.md`](../scripts/testing/TESTING.md) - Документация по тестированию

## Генерация документации

### OpenAPI и gRPC документация

Для автоматической генерации документации из FastAPI сервисов и gRPC proto файлов:

```bash
python3 scripts/generate_openapi.py
```

**Созданные файлы:**
- `openapi/openapi_combined.yaml` - объединенная документация REST API
- `openapi/api_gateway_openapi.yaml` - только API Gateway
- `openapi/user_service_openapi.yaml` - только User Service
- `openapi/grpc_services.md` - документация gRPC сервисов (Post Service, Statistics Service)

### Архитектурные диаграммы

Для просмотра C4 диаграммы используйте [Structurizr](https://structurizr.com/) или совместимые инструменты.

Для просмотра ER диаграммы используйте PlantUML:

```bash
plantuml docs/er.puml
```

## Обновление документации

Документация автоматически обновляется при изменении кода:
- OpenAPI спецификации генерируются из FastAPI приложений
- gRPC документация извлекается из proto файлов
- Архитектурные диаграммы обновляются вручную при изменении архитектуры