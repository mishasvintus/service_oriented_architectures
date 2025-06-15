#!/usr/bin/env python3
"""
Скрипт для запуска только unit тестов
Использование: python3 test_unit.py
"""

import subprocess
import sys


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
    print("🧪 Запуск Unit тестов...")
    print("=" * 40)
    
    try:
        import pytest
    except ImportError:
        print("❌ Не установлены зависимости для тестов")
        print("Установите зависимости: pip install -r requirements-test.txt")
        sys.exit(1)
    
    services = ["user_service", "post_service", "api_service", "statistics_service"]
    all_passed = True
    
    for service in services:
        print(f"\n🔧 Unit тесты {service}...")
        success, stdout, stderr = run_command(
            f"python3 -m pytest {service}/unit_tests/ -v --tb=short"
        )
        
        if success:
            print(f"✅ {service} unit тесты прошли")
            print(stdout)
        else:
            print(f"❌ {service} unit тесты провалились:")
            print(stderr)
            all_passed = False
    
    if all_passed:
        print("\n🎉 Все unit тесты прошли!")
        sys.exit(0)
    else:
        print("\n💥 Некоторые unit тесты провалились!")
        sys.exit(1)


if __name__ == "__main__":
    main() 