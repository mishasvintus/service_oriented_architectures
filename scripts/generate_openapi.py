#!/usr/bin/env python3
"""
Скрипт для генерации OpenAPI документации из FastAPI приложений
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
    
    print(f"\n✅ Завершено! Успешно обработано {success_count} из {len(services)} сервисов")
    print("\n📁 Созданные файлы:")
    for service in services:
        if Path(service['output']).exists():
            print(f"  - {service['output']}")
    if Path("docs/openapi/openapi_combined.yaml").exists():
        print(f"  - docs/openapi/openapi_combined.yaml")

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