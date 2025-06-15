#!/usr/bin/env python3
"""
Скрипт для генерации OpenAPI документации из FastAPI приложений
и документации для gRPC сервисов
"""

import json
import yaml
import requests
import sys
import os
from pathlib import Path

def generate_from_running_service(url: str, output_file: str):
    """Генерация OpenAPI из запущенного сервиса"""
    try:
        print(f"🔄 Получение OpenAPI JSON из {url}/openapi.json...")
        response = requests.get(f"{url}/openapi.json", timeout=10)
        response.raise_for_status()
        
        openapi_data = response.json()
        
        # Конвертация в YAML
        yaml_content = yaml.dump(
            openapi_data, 
            default_flow_style=False, 
            allow_unicode=True,
            sort_keys=False
        )
        
        # Сохранение в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"✅ OpenAPI YAML сохранен в {output_file}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при подключении к сервису: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def generate_from_code(app_module: str, output_file: str):
    """Генерация OpenAPI напрямую из кода FastAPI"""
    try:
        print(f"🔄 Импорт модуля {app_module}...")
        
        # Добавляем текущую директорию в путь
        sys.path.insert(0, os.getcwd())
        
        # Импортируем модуль
        module_parts = app_module.split('.')
        module = __import__(app_module, fromlist=[module_parts[-1]])
        
        # Получаем FastAPI приложение
        if hasattr(module, 'app'):
            app = module.app
        else:
            print("❌ Не найден объект 'app' в модуле")
            return False
        
        # Получаем OpenAPI схему
        openapi_data = app.openapi()
        
        # Конвертация в YAML
        yaml_content = yaml.dump(
            openapi_data, 
            default_flow_style=False, 
            allow_unicode=True,
            sort_keys=False
        )
        
        # Сохранение в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"✅ OpenAPI YAML сохранен в {output_file}")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Генератор OpenAPI документации")
    print("=" * 40)
    
    # Создаем директорию docs если её нет
    docs_dir = Path("docs/openapi")
    docs_dir.mkdir(exist_ok=True)
    
    services = [
        {
            "name": "API Gateway",
            "url": "http://localhost:8000",
            "module": "api_service.app.main",
            "output": "docs/openapi/api_gateway_openapi.yaml"
        },
        {
            "name": "User Service", 
            "url": "http://localhost:8001",
            "module": "user_service.app.main",
            "output": "docs/openapi/user_service_openapi.yaml"
        }
    ]
    
    # Информация о gRPC сервисах (не имеют OpenAPI)
    grpc_services = [
        {
            "name": "Post Service",
            "port": "50051",
            "protocol": "gRPC",
            "proto_file": "post_service/protos/posts.proto"
        },
        {
            "name": "Statistics Service", 
            "port": "50053",
            "protocol": "gRPC",
            "proto_file": "statistics_service/protos/statistics.proto"
        }
    ]
    
    success_count = 0
    
    for service in services:
        print(f"\n📋 Обработка {service['name']}...")
        
        # Сначала пробуем получить из запущенного сервиса
        if generate_from_running_service(service['url'], service['output']):
            success_count += 1
        else:
            print(f"⚠️  Сервис {service['name']} не запущен, пробуем генерацию из кода...")
            
            # Если сервис не запущен, пробуем генерацию из кода
            if generate_from_code(service['module'], service['output']):
                success_count += 1
            else:
                print(f"❌ Не удалось сгенерировать OpenAPI для {service['name']}")
    
    # Объединяем API Gateway и User Service в один файл
    if success_count > 0:
        print(f"\n🔄 Создание объединенной документации...")
        create_combined_openapi()
    
    # Выводим информацию о gRPC сервисах
    print(f"\n📡 gRPC сервисы (не имеют OpenAPI документации):")
    for grpc_service in grpc_services:
        print(f"  - {grpc_service['name']}: {grpc_service['protocol']} на порту {grpc_service['port']}")
        print(f"    Proto файл: {grpc_service['proto_file']}")
    
    # Создаем документацию по gRPC сервисам
    create_grpc_documentation(grpc_services)
    
    print(f"\n✅ Завершено! Успешно обработано {success_count} из {len(services)} REST сервисов")
    print("\n📁 Созданные файлы:")
    for service in services:
        if Path(service['output']).exists():
            print(f"  - {service['output']}")
    if Path("docs/openapi/openapi_combined.yaml").exists():
        print(f"  - docs/openapi/openapi_combined.yaml")
    if Path("docs/openapi/grpc_services.md").exists():
        print(f"  - docs/openapi/grpc_services.md")

def create_grpc_documentation(grpc_services):
    """Создание документации для gRPC сервисов"""
    try:
        doc_content = """# gRPC Services Documentation

Данный документ содержит информацию о gRPC сервисах в архитектуре Social Media API.

## Обзор

gRPC сервисы используют Protocol Buffers для определения интерфейсов и обмена данными.
В отличие от REST API, они не имеют OpenAPI документации, но предоставляют строго типизированные интерфейсы.

## Сервисы

"""
        
        for service in grpc_services:
            doc_content += f"""### {service['name']}

- **Протокол**: {service['protocol']}
- **Порт**: {service['port']}
- **Proto файл**: `{service['proto_file']}`

"""
            
            # Пытаемся прочитать proto файл для дополнительной информации
            proto_path = Path(service['proto_file'])
            if proto_path.exists():
                try:
                    with open(proto_path, 'r', encoding='utf-8') as f:
                        proto_content = f.read()
                    
                    # Извлекаем service definitions
                    import re
                    services_found = re.findall(r'service\s+(\w+)\s*{([^}]+)}', proto_content, re.DOTALL)
                    
                    if services_found:
                        doc_content += "**Доступные методы:**\n\n"
                        for service_name, service_body in services_found:
                            doc_content += f"#### {service_name}\n\n"
                            
                            # Извлекаем методы
                            methods = re.findall(r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)', service_body)
                            for method_name, request_type, response_type in methods:
                                doc_content += f"- `{method_name}({request_type.strip()}) -> {response_type.strip()}`\n"
                            doc_content += "\n"
                    
                except Exception as e:
                    doc_content += f"*Не удалось прочитать proto файл: {e}*\n\n"
            else:
                doc_content += f"*Proto файл не найден: {service['proto_file']}*\n\n"
        
        doc_content += """## Подключение к gRPC сервисам

Для подключения к gRPC сервисам используйте соответствующие клиентские библиотеки:

```python
import grpc
from generated_pb2 import *
from generated_pb2_grpc import *

# Создание канала
channel = grpc.insecure_channel('localhost:PORT')
stub = ServiceStub(channel)

# Вызов метода
response = stub.Method(Request())
```

## Генерация клиентского кода

Для генерации клиентского кода из proto файлов используйте:

```bash
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. your_service.proto
```
"""
        
        # Сохраняем документацию
        with open("docs/openapi/grpc_services.md", 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print("✅ Документация gRPC сервисов создана: docs/openapi/grpc_services.md")
        
    except Exception as e:
        print(f"❌ Ошибка при создании документации gRPC сервисов: {e}")

def create_combined_openapi():
    """Создание объединенной OpenAPI документации"""
    try:
        combined_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Social Media API",
                "description": "Объединенная документация всех микросервисов",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "API Gateway (Development)"}
            ],
            "paths": {},
            "components": {"schemas": {}}
        }
        
        # Загружаем API Gateway спецификацию
        api_gateway_file = Path("docs/openapi/api_gateway_openapi.yaml")
        if api_gateway_file.exists():
            with open(api_gateway_file, 'r', encoding='utf-8') as f:
                api_gateway_spec = yaml.safe_load(f)
            
            # Добавляем пути и схемы из API Gateway
            if 'paths' in api_gateway_spec:
                combined_spec['paths'].update(api_gateway_spec['paths'])
            if 'components' in api_gateway_spec and 'schemas' in api_gateway_spec['components']:
                combined_spec['components']['schemas'].update(api_gateway_spec['components']['schemas'])
        
        # Сохраняем объединенную спецификацию
        yaml_content = yaml.dump(
            combined_spec, 
            default_flow_style=False, 
            allow_unicode=True,
            sort_keys=False
        )
        
        with open("docs/openapi/openapi_combined.yaml", 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print("✅ Объединенная документация создана: docs/openapi/openapi_combined.yaml")
        
    except Exception as e:
        print(f"❌ Ошибка при создании объединенной документации: {e}")

if __name__ == "__main__":
    main() 