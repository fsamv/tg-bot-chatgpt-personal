#!/bin/bash

# Telegram ChatGPT Bot Docker Runner
# Этот скрипт помогает запустить бота в Docker контейнере

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker не запущен или у вас нет прав. Запустите Docker и попробуйте снова."
        exit 1
    fi
    
    print_success "Docker найден и работает"
}

# Проверка наличия docker-compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose не установлен. Установите docker-compose и попробуйте снова."
        exit 1
    fi
    
    print_success "docker-compose найден"
}

# Проверка переменных окружения
check_environment() {
    if [ ! -f .env ]; then
        print_error "Файл .env не найден. Создайте его на основе config.env.example"
        exit 1
    fi
    
    # Загружаем переменные из .env
    source .env
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        print_error "TELEGRAM_BOT_TOKEN не установлен в .env"
        exit 1
    fi
    
    if [ -z "$CHATGPT_EMAIL" ] || [ -z "$CHATGPT_PASSWORD" ]; then
        print_error "CHATGPT_EMAIL или CHATGPT_PASSWORD не установлены в .env"
        exit 1
    fi
    
    print_success "Переменные окружения проверены"
}

# Создание директорий
create_directories() {
    mkdir -p logs
    print_success "Директории созданы"
}

# Сборка образа
build_image() {
    print_message "Сборка Docker образа..."
    docker-compose build
    print_success "Образ собран"
}

# Запуск контейнера
start_container() {
    print_message "Запуск контейнера..."
    docker-compose up -d
    print_success "Контейнер запущен"
}

# Проверка статуса
check_status() {
    print_message "Проверка статуса контейнера..."
    sleep 5
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Контейнер работает"
        print_message "Логи контейнера:"
        docker-compose logs --tail=20
    else
        print_error "Контейнер не запустился"
        docker-compose logs
        exit 1
    fi
}

# Основная функция
main() {
    echo "🤖 Telegram ChatGPT Bot Docker Runner"
    echo "====================================="
    
    check_docker
    check_docker_compose
    check_environment
    create_directories
    build_image
    start_container
    check_status
    
    echo ""
    print_success "Бот успешно запущен в Docker!"
    echo ""
    echo "📋 Полезные команды:"
    echo "  docker-compose logs -f          # Просмотр логов в реальном времени"
    echo "  docker-compose stop             # Остановка контейнера"
    echo "  docker-compose restart          # Перезапуск контейнера"
    echo "  docker-compose down             # Остановка и удаление контейнера"
    echo "  docker-compose ps               # Статус контейнера"
    echo ""
    echo "📁 Логи доступны в директории ./logs"
}

# Обработка аргументов командной строки
case "${1:-}" in
    "stop")
        print_message "Остановка контейнера..."
        docker-compose down
        print_success "Контейнер остановлен"
        ;;
    "restart")
        print_message "Перезапуск контейнера..."
        docker-compose restart
        print_success "Контейнер перезапущен"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        print_message "Очистка Docker ресурсов..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Очистка завершена"
        ;;
    "help")
        echo "Использование: $0 [команда]"
        echo ""
        echo "Команды:"
        echo "  (без аргументов) - Запуск бота"
        echo "  stop             - Остановка бота"
        echo "  restart          - Перезапуск бота"
        echo "  logs             - Просмотр логов"
        echo "  status           - Статус контейнера"
        echo "  clean            - Очистка Docker ресурсов"
        echo "  help             - Показать эту справку"
        ;;
    *)
        main
        ;;
esac 