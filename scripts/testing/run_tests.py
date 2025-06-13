#!/usr/bin/env python3
"""
Скрипт для запуска тестов микросервисной архитектуры
Использование: python3 run_tests.py [unit|integration|kafka|all]
"""

import sys
import subprocess
import os
import time
import requests
from pathlib import Path


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


def check_test_dependencies():
    """Проверяет что зависимости для тестов установлены"""
    try:
        import pytest
        import httpx
        import requests
        return True
    except ImportError as e:
        print(f"❌ Не установлены зависимости для тестов: {e}")
        print("Установите зависимости: pip install -r requirements-test.txt")
        return False


def run_unit_tests():
    """Запускает unit тесты"""
    print("🧪 Запуск Unit тестов...")
    print("=" * 40)
    
    test_files = [
        ("test_unit.py", "все unit тесты"),
    ]
    all_passed = True
    
    for test_file, description in test_files:
        print(f"\n🔧 Запуск {description}...")
        success, stdout, stderr = run_command(
            f"python3 scripts/testing/{test_file}"
        )
        
        if success:
            print(f"✅ {description} прошли")
        else:
            print(f"❌ {description} провалились:")
            print(stderr)
            all_passed = False
    
    return all_passed


def run_integration_tests():
    """Запускает интеграционные тесты"""
    print("🧪 Запуск интеграционных тестов...")
    print("=" * 40)
    
    if not check_services():
        return False
    
    test_files = [
        ("test_integration.py", "все интеграционные тесты"),
    ]
    all_passed = True
    
    for test_file, description in test_files:
        print(f"\n🔧 Запуск {description}...")
        success, stdout, stderr = run_command(
            f"python3 scripts/testing/{test_file}"
        )
        
        if success:
            print(f"✅ {description} прошли")
        else:
            print(f"❌ {description} провалились:")
            print(stderr)
            all_passed = False
    
    return all_passed


def run_kafka_tests():
    """Запускает Kafka тесты"""
    print("🧪 Запуск Kafka интеграционных тестов...")
    print("=" * 40)
    
    if not check_services():
        return False
    
    print("\n🔧 Kafka интеграционные тесты...")
    success, stdout, stderr = run_command(
        "python3 -m pytest tests/test_kafka_integration.py -v --tb=short -s"
    )
    
    if success:
        print("✅ Kafka тесты прошли")
        return True
    else:
        print("❌ Kafka тесты провалились:")
        print(stderr)
        return False


def main():
    """Главная функция"""
    # Переходим в корень проекта (на 2 уровня вверх от scripts/testing/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    
    if len(sys.argv) < 2:
        test_type = "all"
    else:
        test_type = sys.argv[1].lower()
    
    print("🚀 Запуск тестов микросервисной архитектуры")
    print("=" * 50)
    print(f"Тип тестов: {test_type}\n")
    
    if not check_test_dependencies():
        sys.exit(1)
    
    results = {}
    
    if test_type in ["unit", "all"]:
        results["unit"] = run_unit_tests()
        print()
    
    if test_type in ["integration", "all"]:
        results["integration"] = run_integration_tests()
        print()
    
    if test_type in ["kafka", "all"]:
        results["kafka"] = run_kafka_tests()
        print()
    
    print("🎉 Сводка результатов:")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ ПРОШЛИ" if passed else "❌ ПРОВАЛИЛИСЬ"
        print(f"{test_name.capitalize()} тесты: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n💥 Некоторые тесты провалились!")
        sys.exit(1)


if __name__ == "__main__":
    main() 