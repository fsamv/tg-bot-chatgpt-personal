#!/bin/bash

# Скрипт для проверки совместимости Chromium и chromedriver

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

echo "🔍 Проверка совместимости Chromium"
echo "=================================="

# Проверка наличия Chromium
CHROMIUM_PATH=""
if command -v chromium &> /dev/null; then
    CHROMIUM_PATH="chromium"
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_PATH="chromium-browser"
fi

if [ -n "$CHROMIUM_PATH" ]; then
    CHROMIUM_VERSION=$($CHROMIUM_PATH --version | head -n1 | cut -d' ' -f2)
    print_success "Chromium найден: версия $CHROMIUM_VERSION ($CHROMIUM_PATH)"
else
    print_error "Chromium не найден"
    echo "Установите Chromium:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-browser"
    echo "  Fedora/RHEL: sudo dnf install chromium"
    echo "  Arch: sudo pacman -S chromium"
    exit 1
fi

# Проверка наличия chromedriver
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version | cut -d' ' -f2)
    print_success "chromedriver найден: версия $CHROMEDRIVER_VERSION"
else
    print_error "chromedriver не найден"
    echo "Установите chromedriver: sudo apt-get install chromium-driver"
    exit 1
fi

# Проверка совместимости версий
echo ""
print_message "Проверка совместимости версий..."

# Извлекаем мажорную версию
CHROMIUM_MAJOR=$(echo $CHROMIUM_VERSION | cut -d'.' -f1)
CHROMEDRIVER_MAJOR=$(echo $CHROMEDRIVER_VERSION | cut -d'.' -f1)

if [ "$CHROMIUM_MAJOR" = "$CHROMEDRIVER_MAJOR" ]; then
    print_success "Версии совместимы (мажорная версия: $CHROMIUM_MAJOR)"
else
    print_warning "Версии могут быть несовместимы"
    echo "   Chromium: $CHROMIUM_VERSION (мажорная: $CHROMIUM_MAJOR)"
    echo "   chromedriver: $CHROMEDRIVER_VERSION (мажорная: $CHROMEDRIVER_MAJOR)"
    echo ""
    echo "Рекомендации:"
    echo "1. Обновите chromedriver до версии $CHROMIUM_MAJOR.x.x"
    echo "2. Или обновите Chromium до версии $CHROMEDRIVER_MAJOR.x.x"
fi

# Проверка символической ссылки
echo ""
print_message "Проверка символической ссылки..."

if [ -L /usr/bin/google-chrome-stable ]; then
    LINK_TARGET=$(readlink /usr/bin/google-chrome-stable)
    if [ "$LINK_TARGET" = "/usr/bin/chromium" ] || [ "$LINK_TARGET" = "/usr/bin/chromium-browser" ]; then
        print_success "Символическая ссылка настроена правильно"
    else
        print_warning "Символическая ссылка указывает на: $LINK_TARGET"
    fi
else
    print_warning "Символическая ссылка не найдена"
    echo "Создать ссылку? (y/n): "
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$CHROMIUM_PATH" = "chromium" ]; then
            sudo ln -sf /usr/bin/chromium /usr/bin/google-chrome-stable
        elif [ "$CHROMIUM_PATH" = "chromium-browser" ]; then
            sudo ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome-stable
        fi
        print_success "Символическая ссылка создана"
    fi
fi

# Проверка прав доступа
echo ""
print_message "Проверка прав доступа..."

if [ -r /usr/bin/chromium ] && [ -x /usr/bin/chromium ]; then
    print_success "Chromium доступен для чтения и выполнения"
elif [ -r /usr/bin/chromium-browser ] && [ -x /usr/bin/chromium-browser ]; then
    print_success "Chromium-browser доступен для чтения и выполнения"
else
    print_error "Проблемы с правами доступа к Chromium"
fi

if [ -r /usr/bin/chromedriver ] && [ -x /usr/bin/chromedriver ]; then
    print_success "chromedriver доступен для чтения и выполнения"
else
    print_error "Проблемы с правами доступа к chromedriver"
fi

# Тест запуска Chromium в headless режиме
echo ""
print_message "Тест запуска Chromium в headless режиме..."

if timeout 10s $CHROMIUM_PATH --headless --no-sandbox --disable-dev-shm-usage --disable-gpu --dump-dom https://www.google.com > /dev/null 2>&1; then
    print_success "Chromium успешно запускается в headless режиме"
else
    print_warning "Проблемы с запуском Chromium в headless режиме"
    echo "Это может быть связано с:"
    echo "1. Отсутствием дисплея (нормально для серверов)"
    echo "2. Недостатком памяти"
    echo "3. Проблемами с правами доступа"
fi

# Проверка Python зависимостей
echo ""
print_message "Проверка Python зависимостей..."

if python3 -c "import selenium" 2>/dev/null; then
    SELENIUM_VERSION=$(python3 -c "import selenium; print(selenium.__version__)" 2>/dev/null)
    print_success "Selenium установлен: версия $SELENIUM_VERSION"
else
    print_error "Selenium не установлен"
    echo "Установите: pip install selenium"
fi

if python3 -c "import webdriver_manager" 2>/dev/null; then
    print_success "webdriver-manager установлен"
else
    print_warning "webdriver-manager не установлен"
    echo "Установите: pip install webdriver-manager"
fi

echo ""
print_success "Проверка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Если все проверки пройдены, можете запускать бота"
echo "2. Если есть предупреждения, исправьте их перед запуском"
echo "3. Для запуска: python telegram_bot.py" 