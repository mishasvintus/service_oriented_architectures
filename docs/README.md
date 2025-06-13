# Документация проекта

Эта директория содержит всю техническую документацию социальной сети.

## Содержание

### Архитектура
- [`social_media.c4`](social_media.c4) - C4 диаграмма архитектуры

### База данных
- [`er.puml`](er.puml) - ER диаграмма базы данных

### API
- [`openapi.yaml`](openapi.yaml) - OpenAPI 3.0 спецификация REST API (ручная)
- [`openapi_combined.yaml`](openapi_combined.yaml) - Автогенерированная OpenAPI спецификация
- [`api_gateway_openapi.yaml`](api_gateway_openapi.yaml) - OpenAPI для API Gateway
- [`user_service_openapi.yaml`](user_service_openapi.yaml) - OpenAPI для User Service

### Тестирование
- [`../scripts/testing/TESTING.md`](../scripts/testing/TESTING.md) - Документация по тестированию

## Генерация OpenAPI

Для автоматической генерации OpenAPI документации из FastAPI сервисов:

```bash
python3 scripts/generate_openapi.py
```

**Созданные файлы:**
- `openapi_combined.yaml` - объединенная документация всех сервисов
- `api_gateway_openapi.yaml` - только API Gateway
- `user_service_openapi.yaml` - только User Service

## Обновление документации