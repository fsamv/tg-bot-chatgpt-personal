#!/bin/bash

# Telegram ChatGPT Bot Setup Script для CentOS Stream 9
# Этот скрипт автоматически устанавливает и настраивает бота на CentOS Stream 9

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🤖 Установка Telegram ChatGPT Bot для CentOS Stream 9"
echo "====================================================="

# Проверка операционной системы
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "Этот скрипт предназначен только для Linux"
    exit 1
fi

# Проверка версии CentOS
if [ -f /etc/redhat-release ]; then
    CENTOS_VERSION=$(cat /etc/redhat-release)
    print_message "Обнаружена система: $CENTOS_VERSION"
    
    if [[ "$CENTOS_VERSION" != *"CentOS Stream 9"* ]]; then
        print_warning "Этот скрипт оптимизирован для CentOS Stream 9"
        print_warning "Текущая система: $CENTOS_VERSION"
        read -p "Продолжить установку? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_error "Этот скрипт предназначен для CentOS/RHEL систем"
    exit 1
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 не установлен. Устанавливаем..."
    sudo dnf update -y
    sudo dnf install -y python3 python3-pip python3-venv
else
    print_success "Python 3 найден"
fi

# Установка EPEL репозитория
print_message "Установка EPEL репозитория..."
if ! sudo dnf list installed | grep -q epel-release; then
    sudo dnf install -y epel-release
    print_success "EPEL репозиторий установлен"
else
    print_success "EPEL репозиторий уже установлен"
fi

# Установка Chromium
print_message "Установка Chromium..."
if sudo dnf install -y chromium chromedriver 2>/dev/null; then
    print_success "Chromium установлен из EPEL репозитория"
else
    print_warning "Chromium не найден в EPEL. Попытка установки через snap..."
    
    # Установка snapd
    if ! command -v snap &> /dev/null; then
        print_message "Установка snapd..."
        sudo dnf install -y snapd
        sudo systemctl enable --now snapd.socket
        sudo ln -s /var/lib/snapd/snap /snap
        print_success "snapd установлен и запущен"
    fi
    
    # Установка Chromium через snap
    if sudo snap install chromium; then
        print_success "Chromium установлен через snap"
        
        # Установка chromedriver отдельно
        if sudo dnf install -y chromedriver 2>/dev/null; then
            print_success "chromedriver установлен"
        else
            print_warning "chromedriver не найден в репозиториях"
            print_message "Будет использован webdriver-manager для автоматической загрузки chromedriver"
        fi
    else
        print_error "Не удалось установить Chromium"
        print_message "Попробуйте установить вручную:"
        print_message "   sudo dnf install -y epel-release"
        print_message "   sudo dnf install -y chromium chromedriver"
        exit 1
    fi
fi

# Создание виртуального окружения
print_message "Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
print_success "Виртуальное окружение создано"

# Установка зависимостей
print_message "Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Зависимости установлены"

# Проверка совместимости Chromium
print_message "Проверка совместимости Chromium..."

# Определяем путь к Chromium
CHROMIUM_PATH=""
if command -v chromium &> /dev/null; then
    CHROMIUM_PATH="chromium"
elif command -v snap &> /dev/null && snap list | grep -q chromium; then
    CHROMIUM_PATH="snap run chromium"
fi

if [ -n "$CHROMIUM_PATH" ] && command -v chromedriver &> /dev/null; then
    CHROMIUM_VERSION=$($CHROMIUM_PATH --version | head -n1 | cut -d' ' -f2)
    CHROMEDRIVER_VERSION=$(chromedriver --version | cut -d' ' -f2)
    print_success "Chromium версия: $CHROMIUM_VERSION"
    print_success "chromedriver версия: $CHROMEDRIVER_VERSION"
    
    # Проверяем совместимость версий
    if [[ "$CHROMIUM_VERSION" != "$CHROMEDRIVER_VERSION" ]]; then
        print_warning "Версии Chromium и chromedriver не совпадают"
        print_warning "   Chromium: $CHROMIUM_VERSION"
        print_warning "   chromedriver: $CHROMEDRIVER_VERSION"
        print_warning "   Это может вызвать проблемы. Рекомендуется обновить chromedriver"
    fi
else
    print_warning "Chromium или chromedriver не найдены"
    print_message "Будет использован webdriver-manager для автоматической загрузки"
fi

# Создание файла конфигурации
if [ ! -f .env ]; then
    print_message "Создание файла конфигурации..."
    cp config.env.example .env
    print_success "Файл конфигурации создан"
    print_message "📝 Отредактируйте файл .env и укажите ваши данные:"
    print_message "   - TELEGRAM_BOT_TOKEN (получите у @BotFather)"
    print_message "   - CHATGPT_EMAIL"
    print_message "   - CHATGPT_PASSWORD"
else
    print_success "Файл конфигурации уже существует"
fi

# Выбор типа установки
echo ""
print_message "🔧 Выберите тип установки:"
echo "1. Обычная установка (рекомендуется для разработки)"
echo "2. Оптимизированная установка (рекомендуется для продакшена)"
read -p "Выберите вариант (1/2): " -n 1 -r
echo

if [[ $REPLY =~ ^[2]$ ]]; then
    print_message "🚀 Оптимизированная установка..."
    print_message "📦 Установка дополнительных оптимизаций..."
    
    # Создаем символическую ссылку для совместимости
    if [ ! -L /usr/bin/google-chrome-stable ]; then
        if [ "$CHROMIUM_PATH" = "chromium" ]; then
            sudo ln -sf /usr/bin/chromium /usr/bin/google-chrome-stable
            print_success "Создана символическая ссылка для совместимости (chromium)"
        elif [ "$CHROMIUM_PATH" = "snap run chromium" ]; then
            sudo ln -sf /snap/bin/chromium /usr/bin/google-chrome-stable
            print_success "Создана символическая ссылка для совместимости (snap chromium)"
        fi
    fi
    
    # Создаем директории для логов
    mkdir -p logs
    print_success "Создана директория для логов"
    
    print_message "📋 Для запуска используйте:"
    print_message "   python telegram_bot.py"
    print_message "   или Docker: docker compose -f docker-compose.optimized.yml up -d"
else
    print_message "📦 Обычная установка..."
    print_message "📋 Для запуска используйте:"
    print_message "   python telegram_bot.py"
    print_message "   или Docker: docker compose up -d"
fi

# Создание systemd сервиса (опционально)
read -p "Создать systemd сервис для автозапуска? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_message "🔧 Создание systemd сервиса..."
    
    # Получение пути к проекту
    PROJECT_PATH=$(pwd)
    USER_NAME=$(whoami)
    VENV_PATH="$PROJECT_PATH/venv"
    
    # Создание файла сервиса
    sudo tee /etc/systemd/system/telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram ChatGPT Bot
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_PATH
Environment=PATH=$VENV_PATH/bin
ExecStart=$VENV_PATH/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Перезагрузка systemd и включение сервиса
    sudo systemctl daemon-reload
    sudo systemctl enable telegram-bot
    
    print_success "Systemd сервис создан и включен"
    print_message "📋 Команды для управления сервисом:"
    print_message "   sudo systemctl start telegram-bot    # Запуск"
    print_message "   sudo systemctl stop telegram-bot     # Остановка"
    print_message "   sudo systemctl status telegram-bot   # Статус"
    print_message "   sudo systemctl restart telegram-bot  # Перезапуск"
    print_message "   sudo journalctl -u telegram-bot -f   # Просмотр логов"
fi

echo ""
print_success "🎉 Установка завершена!"
echo ""
print_message "📋 Следующие шаги:"
print_message "1. Отредактируйте файл .env с вашими данными"
print_message "2. Запустите бота: python telegram_bot.py"
print_message "3. Или используйте systemd сервис (если создан)"
echo ""
print_message "🔧 Дополнительные команды:"
print_message "   # Проверка версий"
print_message "   $CHROMIUM_PATH --version"
print_message "   chromedriver --version"
echo ""
print_message "   # Запуск в Docker (обычный)"
print_message "   docker compose up -d"
echo ""
print_message "   # Запуск в Docker (оптимизированный)"
print_message "   docker compose -f docker-compose.optimized.yml up -d"
echo ""
print_message "   # Просмотр логов"
print_message "   docker compose logs -f"
echo ""
print_message "📚 Дополнительная информация:"
print_message "   - README.md - основная документация"
print_message "   - DOCKER_README.md - Docker развертывание"
print_message "   - DOCKER_OPTIMIZATION.md - оптимизация образов" 