#!/bin/bash

# Скрипт для запуска тестов микросервисной архитектуры
# Использование: scripts/run_tests.sh [unit|integration|kafka|all]

# Переходим в корень проекта (на 1 уровень вверх от scripts/)
cd "$(dirname "$0")/.."
python3 scripts/testing/run_tests.py "$@" 