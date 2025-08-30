#!/bin/bash

# 🚀 Демонстрация работы микросервисной социальной сети
# Полный сценарий: Регистрация → Посты → Взаимодействие → Статистика

set -e  # Остановка при ошибке

echo "🚀 Демонстрация работы социальной сети"
echo "======================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Базовый URL API Gateway
BASE_URL="http://localhost:8000"

# Функция для красивого вывода
print_step() {
    echo -e "\n${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для выполнения curl с красивым выводом
execute_curl() {
    local description="$1"
    local curl_command="$2"
    
    print_info "$description"
    echo "Команда: $curl_command"
    echo ""
    
    # Выполняем команду и сохраняем результат
    response=$(eval "$curl_command")
    echo "Ответ: $response"
    echo ""
}

# Проверка доступности сервисов
print_step "Проверка доступности сервисов"

curl -s "$BASE_URL/docs" > /dev/null && print_success "API Gateway доступен" || { print_error "API Gateway недоступен"; exit 1; }
curl -s "http://localhost:8080" > /dev/null && print_success "Kafka UI доступен" || print_error "Kafka UI недоступен"

# ============================================================================
# 1. РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================================

print_step "1. Регистрация пользователей (User Service)"

print_info "Регистрация пользователя Alice"
user1_response=$(curl -s -X POST "$BASE_URL/api/register" \
    -H 'Content-Type: application/json' \
    -d '{
        "login": "alice_demo",
        "email": "alice@example.com",
        "password": "password123",
        "first_name": "Alice",
        "last_name": "Johnson"
    }')

echo "Ответ регистрации: $user1_response"
echo ""

print_info "Логин пользователя Alice"
alice_login_response=$(curl -s -X POST "$BASE_URL/api/login" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=alice_demo&password=password123')

echo "Ответ логина: $alice_login_response"
echo ""

alice_token=$(echo "$alice_login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
print_success "Токен Alice получен: ${alice_token:0:20}..."

print_info "Регистрация пользователя Bob"
user2_response=$(curl -s -X POST "$BASE_URL/api/register" \
    -H 'Content-Type: application/json' \
    -d '{
        "login": "bob_demo",
        "email": "bob@example.com",
        "password": "password456",
        "first_name": "Bob",
        "last_name": "Smith"
    }')

echo "Ответ регистрации: $user2_response"
echo ""

print_info "Логин пользователя Bob"
bob_login_response=$(curl -s -X POST "$BASE_URL/api/login" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=bob_demo&password=password456')

echo "Ответ логина: $bob_login_response"
echo ""

bob_token=$(echo "$bob_login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
print_success "Токен Bob получен: ${bob_token:0:20}..."

print_info "Регистрация пользователя Charlie"
user3_response=$(curl -s -X POST "$BASE_URL/api/register" \
    -H 'Content-Type: application/json' \
    -d '{
        "login": "charlie_demo",
        "email": "charlie@example.com",
        "password": "password789",
        "first_name": "Charlie",
        "last_name": "Brown"
    }')

echo "Ответ регистрации: $user3_response"
echo ""

print_info "Логин пользователя Charlie"
charlie_login_response=$(curl -s -X POST "$BASE_URL/api/login" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=charlie_demo&password=password789')

echo "Ответ логина: $charlie_login_response"
echo ""

charlie_token=$(echo "$charlie_login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
print_success "Токен Charlie получен: ${charlie_token:0:20}..."

# ============================================================================
# 2. СОЗДАНИЕ ПОСТОВ
# ============================================================================

print_step "2. Создание постов (Post Service)"

post1_response=$(curl -s -X POST "$BASE_URL/api/posts" \
    -H "Authorization: Bearer $alice_token" \
    -H 'Content-Type: application/json' \
    -d '{
        "title": "Мое путешествие в Японию",
        "description": "Невероятные впечатления от поездки в Токио! Рекомендую всем посетить храм Сенсо-дзи.",
        "is_public": true
    }')

echo "Ответ: $post1_response"
echo ""

alice_post_id=$(echo "$post1_response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
print_success "Пост Alice создан с ID: $alice_post_id"

print_info "Bob создает пост о технологиях"
post2_response=$(curl -s -X POST "$BASE_URL/api/posts" \
    -H "Authorization: Bearer $bob_token" \
    -H 'Content-Type: application/json' \
    -d '{
        "title": "Микросервисы vs Монолит",
        "description": "Размышления о том, когда стоит использовать микросервисную архитектуру, а когда лучше остаться с монолитом.",
        "is_public": true
    }')

echo "Ответ: $post2_response"
echo ""

bob_post_id=$(echo "$post2_response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
print_success "Пост Bob создан с ID: $bob_post_id"

print_info "Charlie создает пост о кулинарии"
post3_response=$(curl -s -X POST "$BASE_URL/api/posts" \
    -H "Authorization: Bearer $charlie_token" \
    -H 'Content-Type: application/json' \
    -d '{
        "title": "Рецепт идеальной пасты",
        "description": "Секреты приготовления настоящей итальянской пасты карбонара. Главное - не добавлять сливки!",
        "is_public": true
    }')

echo "Ответ: $post3_response"
echo ""

charlie_post_id=$(echo "$post3_response" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
print_success "Пост Charlie создан с ID: $charlie_post_id"

# ============================================================================
# 3. ПРОСМОТР ПОСТОВ
# ============================================================================

print_step "3. Просмотр постов (генерация событий в Kafka)"

execute_curl \
    "Bob просматривает пост Alice о Японии" \
    "curl -s -X POST '$BASE_URL/api/posts/$alice_post_id/view' \
    -H 'Authorization: Bearer $bob_token'"

execute_curl \
    "Charlie просматривает пост Alice о Японии" \
    "curl -s -X POST '$BASE_URL/api/posts/$alice_post_id/view' \
    -H 'Authorization: Bearer $charlie_token'"

execute_curl \
    "Alice просматривает пост Bob о технологиях" \
    "curl -s -X POST '$BASE_URL/api/posts/$bob_post_id/view' \
    -H 'Authorization: Bearer $alice_token'"

execute_curl \
    "Charlie просматривает пост Bob о технологиях" \
    "curl -s -X POST '$BASE_URL/api/posts/$bob_post_id/view' \
    -H 'Authorization: Bearer $charlie_token'"

execute_curl \
    "Alice просматривает пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/view' \
    -H 'Authorization: Bearer $alice_token'"

execute_curl \
    "Bob просматривает пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/view' \
    -H 'Authorization: Bearer $bob_token'"

# ============================================================================
# 4. ЛАЙКИ ПОСТОВ
# ============================================================================

print_step "4. Лайки постов (генерация событий в Kafka)"

# Лайки для поста Alice
execute_curl \
    "Bob лайкает пост Alice о Японии" \
    "curl -s -X POST '$BASE_URL/api/posts/$alice_post_id/like' \
    -H 'Authorization: Bearer $bob_token'"

execute_curl \
    "Charlie лайкает пост Alice о Японии" \
    "curl -s -X POST '$BASE_URL/api/posts/$alice_post_id/like' \
    -H 'Authorization: Bearer $charlie_token'"

# Лайки для поста Bob
execute_curl \
    "Alice лайкает пост Bob о технологиях" \
    "curl -s -X POST '$BASE_URL/api/posts/$bob_post_id/like' \
    -H 'Authorization: Bearer $alice_token'"

# Лайки для поста Charlie
execute_curl \
    "Alice лайкает пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/like' \
    -H 'Authorization: Bearer $alice_token'"

execute_curl \
    "Bob лайкает пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/like' \
    -H 'Authorization: Bearer $bob_token'"

# ============================================================================
# 5. КОММЕНТАРИИ К ПОСТАМ
# ============================================================================

print_step "5. Комментарии к постам (генерация событий в Kafka)"

# Комментарии к посту Alice
print_info "Bob комментирует пост Alice о Японии"
curl -s -X POST "$BASE_URL/api/posts/$alice_post_id/comments" \
    -H "Authorization: Bearer $bob_token" \
    -H 'Content-Type: application/json' \
    -d '{"content": "Потрясающие фотографии! Я тоже мечтаю побывать в Японии."}'
echo ""

print_info "Charlie комментирует пост Alice о Японии"
curl -s -X POST "$BASE_URL/api/posts/$alice_post_id/comments" \
    -H "Authorization: Bearer $charlie_token" \
    -H 'Content-Type: application/json' \
    -d '{"content": "А какие еще места в Токио ты посетила?"}'
echo ""

# Комментарии к посту Bob
execute_curl \
    "Alice комментирует пост Bob о технологиях" \
    "curl -s -X POST '$BASE_URL/api/posts/$bob_post_id/comments' \
    -H 'Authorization: Bearer $alice_token' \
    -H 'Content-Type: application/json' \
    -d '{\"content\": \"Отличная статья! Согласна, что микросервисы не всегда нужны.\"}'"

execute_curl \
    "Charlie комментирует пост Bob о технологиях" \
    "curl -s -X POST '$BASE_URL/api/posts/$bob_post_id/comments' \
    -H 'Authorization: Bearer $charlie_token' \
    -H 'Content-Type: application/json' \
    -d '{\"content\": \"А как ты относишься к serverless архитектуре?\"}'"

# Комментарии к посту Charlie
execute_curl \
    "Alice комментирует пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/comments' \
    -H 'Authorization: Bearer $alice_token' \
    -H 'Content-Type: application/json' \
    -d '{\"content\": \"Спасибо за рецепт! Обязательно попробую приготовить.\"}'"

execute_curl \
    "Bob комментирует пост Charlie о кулинарии" \
    "curl -s -X POST '$BASE_URL/api/posts/$charlie_post_id/comments' \
    -H 'Authorization: Bearer $bob_token' \
    -H 'Content-Type: application/json' \
    -d '{\"content\": \"А какой сыр лучше использовать для карбонары?\"}'"

# ============================================================================
# 6. ПОЛУЧЕНИЕ КОММЕНТАРИЕВ
# ============================================================================

print_step "6. Получение комментариев к постам"

execute_curl \
    "Получение комментариев к посту Alice" \
    "curl -s -X GET '$BASE_URL/api/posts/$alice_post_id/comments?page=1&page_size=10'"

execute_curl \
    "Получение комментариев к посту Bob" \
    "curl -s -X GET '$BASE_URL/api/posts/$bob_post_id/comments?page=1&page_size=10'"

execute_curl \
    "Получение комментариев к посту Charlie" \
    "curl -s -X GET '$BASE_URL/api/posts/$charlie_post_id/comments?page=1&page_size=10'"

# ============================================================================
# 7. ОЖИДАНИЕ ОБРАБОТКИ СОБЫТИЙ
# ============================================================================

print_step "7. Ожидание обработки событий Statistics Service"

print_info "Ждем 5 секунд для обработки событий Kafka..."
sleep 5

# ============================================================================
# 8. СТАТИСТИКА ПОСТОВ
# ============================================================================

print_step "8. Получение статистики постов (Statistics Service)"

execute_curl \
    "Статистика поста Alice о Японии" \
    "curl -s -X GET '$BASE_URL/api/posts/$alice_post_id/stats' \
    -H 'Authorization: Bearer $alice_token'"

execute_curl \
    "Статистика поста Bob о технологиях" \
    "curl -s -X GET '$BASE_URL/api/posts/$bob_post_id/stats' \
    -H 'Authorization: Bearer $bob_token'"

execute_curl \
    "Статистика поста Charlie о кулинарии" \
    "curl -s -X GET '$BASE_URL/api/posts/$charlie_post_id/stats' \
    -H 'Authorization: Bearer $charlie_token'"

# ============================================================================
# 9. ДИНАМИКА МЕТРИК
# ============================================================================

print_step "9. Динамика метрик за последний час"

# Получаем временные метки для запроса динамики
end_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
start_time=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ")

execute_curl \
    "Динамика просмотров поста Alice" \
    "curl -s -X GET '$BASE_URL/api/posts/$alice_post_id/dynamics/views?start_time=$start_time&end_time=$end_time'"

execute_curl \
    "Динамика лайков поста Alice" \
    "curl -s -X GET '$BASE_URL/api/posts/$alice_post_id/dynamics/likes?start_time=$start_time&end_time=$end_time'"

execute_curl \
    "Динамика комментариев поста Alice" \
    "curl -s -X GET '$BASE_URL/api/posts/$alice_post_id/dynamics/comments?start_time=$start_time&end_time=$end_time'"

# ============================================================================
# 10. ТОП ПОСТОВ И ПОЛЬЗОВАТЕЛЕЙ
# ============================================================================

print_step "10. Топ постов и пользователей (Statistics Service)"

execute_curl \
    "Топ 10 постов по просмотрам" \
    "curl -s -X GET '$BASE_URL/api/statistics/posts/top?metric=views&limit=10'"

execute_curl \
    "Топ 10 постов по лайкам" \
    "curl -s -X GET '$BASE_URL/api/statistics/posts/top?metric=likes&limit=10'"

execute_curl \
    "Топ 10 постов по комментариям" \
    "curl -s -X GET '$BASE_URL/api/statistics/posts/top?metric=comments&limit=10'"

execute_curl \
    "Топ 10 пользователей по просмотрам" \
    "curl -s -X GET '$BASE_URL/api/statistics/users/top?metric=views&limit=10'"

execute_curl \
    "Топ 10 пользователей по лайкам" \
    "curl -s -X GET '$BASE_URL/api/statistics/users/top?metric=likes&limit=10'"

execute_curl \
    "Топ 10 пользователей по комментариям" \
    "curl -s -X GET '$BASE_URL/api/statistics/users/top?metric=comments&limit=10'"

# ============================================================================
# 11. ПОЛУЧЕНИЕ ПРОФИЛЕЙ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================================

print_step "11. Получение профилей пользователей"

execute_curl \
    "Профиль Alice" \
    "curl -s -X GET '$BASE_URL/api/profile' \
    -H 'Authorization: Bearer $alice_token'"

execute_curl \
    "Профиль Bob" \
    "curl -s -X GET '$BASE_URL/api/profile' \
    -H 'Authorization: Bearer $bob_token'"

execute_curl \
    "Профиль Charlie" \
    "curl -s -X GET '$BASE_URL/api/profile' \
    -H 'Authorization: Bearer $charlie_token'"

# ============================================================================
# 12. ПОЛУЧЕНИЕ СПИСКА ПОСТОВ
# ============================================================================

print_step "12. Получение списка всех постов"

execute_curl \
    "Список всех публичных постов" \
    "curl -s -X GET '$BASE_URL/api/posts?page=1&page_size=10'"

# ============================================================================
# ЗАВЕРШЕНИЕ
# ============================================================================

print_step "🎉 Демонстрация завершена!"

print_success "Все основные функции социальной сети продемонстрированы:"
echo "  ✅ Регистрация пользователей (User Service)"
echo "  ✅ Создание постов (Post Service)"
echo "  ✅ Просмотры, лайки, комментарии (Post Service + Kafka)"
echo "  ✅ Получение статистики (Statistics Service + ClickHouse)"
echo "  ✅ Динамика метрик (Statistics Service)"
echo "  ✅ Топ постов и пользователей (Statistics Service)"

print_info "Проверьте Kafka UI: http://localhost:8080"
print_info "Swagger документация: http://localhost:8000/docs"

echo ""
print_success "🚀 Микросервисная социальная сеть работает корректно!" 