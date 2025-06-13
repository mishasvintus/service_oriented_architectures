#!/usr/bin/env python3
"""
Скрипт для запуска только интеграционных тестов
Использование: python3 test_integration.py
"""

import subprocess
import sys
import requests


def check_service(url, name):
    """Проверяет доступность сервиса"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} доступен")
            return True
    except:
        pass
    print(f"❌ {name} недоступен на {url}")
    return False


def check_services():
    """Проверяет доступность всех сервисов"""
    print("🔍 Проверка доступности сервисов...")
    
    services = [
        ("http://localhost:8000/health", "API Gateway"),
        ("http://localhost:8001/docs", "User Service"),
        ("http://localhost:8080", "Kafka UI")
    ]
    
    all_available = True
    for url, name in services:
        if not check_service(url, name):
            all_available = False
    
    if not all_available:
        print("\n❌ Не все сервисы доступны. Запустите: docker-compose up -d")
        return False
    
    print("✅ Все сервисы доступны\n")
    return True


def run_command(command, cwd=None):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    print("🧪 Запуск интеграционных тестов...")
    print("=" * 40)
    
    if not check_services():
        sys.exit(1)
    
    try:
        import pytest
        import httpx
    except ImportError:
        print("❌ Не установлены зависимости для тестов")
        print("Установите зависимости: pip install -r requirements-test.txt")
        sys.exit(1)
    
    services = ["user_service", "post_service", "api_service"]
    all_passed = True
    
    for service in services:
        print(f"\n🔧 Интеграционные тесты {service}...")
        success, stdout, stderr = run_command(
            "python3 -m pytest integrational_tests/ -v --tb=short", 
            cwd=service
        )
        
        if success:
            print(f"✅ {service} интеграционные тесты прошли")
            print(stdout)
        else:
            print(f"❌ {service} интеграционные тесты провалились:")
            print(stderr)
            all_passed = False
    
    if all_passed:
        print("\n🎉 Все интеграционные тесты прошли!")
        sys.exit(0)
    else:
        print("\n💥 Некоторые интеграционные тесты провалились!")
        sys.exit(1)


if __name__ == "__main__":
    main() 