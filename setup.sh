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

# Проверка Chrome
if ! command -v google-chrome &> /dev/null; then
    echo "❌ Google Chrome не установлен. Устанавливаем..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
else
    echo "✅ Google Chrome найден"
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

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
echo "📚 Дополнительная информация в README.md" 