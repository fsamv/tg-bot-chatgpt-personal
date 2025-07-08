#!/bin/bash

# Telegram ChatGPT Bot Setup Script
# Этот скрипт автоматически устанавливает и настраивает бота на Linux сервере

set -e

echo "🤖 Установка Telegram ChatGPT Bot"
echo "=================================="

# Проверка операционной системы
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Этот скрипт предназначен только для Linux"
    exit 1
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не установлен. Устанавливаем..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
else
    echo "✅ Python 3 найден"
fi

# Функция для определения дистрибутива
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    else
        echo "unknown"
    fi
}

# Функция для установки Chromium
install_chromium() {
    local distro=$1
    case $distro in
        "ubuntu"|"debian")
            echo "📦 Установка Chromium для Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y chromium-browser chromium-chromedriver
            ;;
        "fedora"|"rhel"|"centos")
            echo "📦 Установка Chromium для Fedora/RHEL/CentOS..."
            sudo dnf update -y
            sudo dnf install -y chromium chromium-headless chromedriver
            ;;
        "arch")
            echo "📦 Установка Chromium для Arch Linux..."
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm chromium chromedriver
            ;;
        *)
            echo "❌ Неподдерживаемый дистрибутив: $distro"
            echo "Попробуйте установить Chromium вручную"
            exit 1
            ;;
    esac
}

# Определяем дистрибутив
DISTRO=$(detect_distro)
echo "🔍 Обнаружен дистрибутив: $DISTRO"

# Проверка Chromium
if ! command -v chromium &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "❌ Chromium не установлен. Устанавливаем..."
    install_chromium $DISTRO
    echo "✅ Chromium установлен"
else
    echo "✅ Chromium найден"
fi

# Проверка chromedriver
if ! command -v chromedriver &> /dev/null; then
    echo "❌ chromedriver не найден. Устанавливаем..."
    case $DISTRO in
        "ubuntu"|"debian")
            sudo apt-get install -y chromium-chromedriver
            ;;
        "fedora"|"rhel"|"centos")
            sudo dnf install -y chromedriver
            ;;
        "arch")
            sudo pacman -S --noconfirm chromedriver
            ;;
    esac
    echo "✅ chromedriver установлен"
else
    echo "✅ chromedriver найден"
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Проверка совместимости Chromium
echo "🔍 Проверка совместимости Chromium..."

# Определяем путь к Chromium
CHROMIUM_PATH=""
if command -v chromium &> /dev/null; then
    CHROMIUM_PATH="chromium"
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_PATH="chromium-browser"
fi

if [ -n "$CHROMIUM_PATH" ] && command -v chromedriver &> /dev/null; then
    CHROMIUM_VERSION=$($CHROMIUM_PATH --version | head -n1 | cut -d' ' -f2)
    CHROMEDRIVER_VERSION=$(chromedriver --version | cut -d' ' -f2)
    echo "✅ Chromium версия: $CHROMIUM_VERSION"
    echo "✅ chromedriver версия: $CHROMEDRIVER_VERSION"
    
    # Проверяем совместимость версий
    if [[ "$CHROMIUM_VERSION" != "$CHROMEDRIVER_VERSION" ]]; then
        echo "⚠️  Версии Chromium и chromedriver не совпадают"
        echo "   Chromium: $CHROMIUM_VERSION"
        echo "   chromedriver: $CHROMEDRIVER_VERSION"
        echo "   Это может вызвать проблемы. Рекомендуется обновить chromedriver"
    fi
else
    echo "❌ Chromium или chromedriver не найдены"
    exit 1
fi

# Создание файла конфигурации
if [ ! -f .env ]; then
    echo "⚙️ Создание файла конфигурации..."
    cp config.env.example .env
    echo "📝 Отредактируйте файл .env и укажите ваши данные:"
    echo "   - TELEGRAM_BOT_TOKEN (получите у @BotFather)"
    echo "   - CHATGPT_EMAIL"
    echo "   - CHATGPT_PASSWORD"
    echo ""
    echo "После настройки запустите: python telegram_bot.py"
else
    echo "✅ Файл конфигурации уже существует"
fi

# Выбор типа установки
echo ""
echo "🔧 Выберите тип установки:"
echo "1. Обычная установка (рекомендуется для разработки)"
echo "2. Оптимизированная установка (рекомендуется для продакшена)"
read -p "Выберите вариант (1/2): " -n 1 -r
echo

if [[ $REPLY =~ ^[2]$ ]]; then
    echo "🚀 Оптимизированная установка..."
    echo "📦 Установка дополнительных оптимизаций..."
    
    # Создаем символическую ссылку для совместимости
    if [ ! -L /usr/bin/google-chrome-stable ]; then
        if command -v chromium &> /dev/null; then
            sudo ln -sf /usr/bin/chromium /usr/bin/google-chrome-stable
            echo "✅ Создана символическая ссылка для совместимости (chromium)"
        elif command -v chromium-browser &> /dev/null; then
            sudo ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome-stable
            echo "✅ Создана символическая ссылка для совместимости (chromium-browser)"
        fi
    fi
    
    # Создаем директории для логов
    mkdir -p logs
    echo "✅ Создана директория для логов"
    
    echo "📋 Для запуска используйте:"
    echo "   python telegram_bot.py"
    echo "   или Docker: docker compose -f docker-compose.optimized.yml up -d"
else
    echo "📦 Обычная установка..."
    echo "📋 Для запуска используйте:"
    echo "   python telegram_bot.py"
    echo "   или Docker: docker compose up -d"
fi

# Создание systemd сервиса (опционально)
read -p "Создать systemd сервис для автозапуска? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Создание systemd сервиса..."
    
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
    
    echo "✅ Systemd сервис создан и включен"
    echo "📋 Команды для управления сервисом:"
    echo "   sudo systemctl start telegram-bot    # Запуск"
    echo "   sudo systemctl stop telegram-bot     # Остановка"
    echo "   sudo systemctl status telegram-bot   # Статус"
    echo "   sudo systemctl restart telegram-bot  # Перезапуск"
    echo "   sudo journalctl -u telegram-bot -f   # Просмотр логов"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env с вашими данными"
echo "2. Запустите бота: python telegram_bot.py"
echo "3. Или используйте systemd сервис (если создан)"
echo ""
echo "🔧 Дополнительные команды:"
echo "   # Проверка версий"
echo "   chromium --version"
echo "   chromedriver --version"
echo ""
echo "   # Запуск в Docker (обычный)"
echo "   docker compose up -d"
echo ""
echo "   # Запуск в Docker (оптимизированный)"
echo "   docker compose -f docker-compose.optimized.yml up -d"
echo ""
echo "   # Просмотр логов"
echo "   docker compose logs -f"
echo ""
echo "📚 Дополнительная информация:"
echo "   - README.md - основная документация"
echo "   - DOCKER_README.md - Docker развертывание"
echo "   - DOCKER_OPTIMIZATION.md - оптимизация образов" 