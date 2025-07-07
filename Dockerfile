# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем метаданные
LABEL maintainer="Telegram ChatGPT Bot"
LABEL description="Telegram bot for ChatGPT integration"
LABEL version="1.0"

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium chromium-driver \
        xvfb \
    && ln -s /usr/bin/chromium /usr/bin/google-chrome-stable \
    && pip install --upgrade pip \
    && apt-get purge -y --auto-remove wget gnupg unzip curl \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/* /var/tmp/* \
    && rm -rf /usr/share/doc /usr/share/man /usr/share/locale /usr/share/zoneinfo

# Создаем пользователя для безопасности
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории для логов и временных файлов
RUN mkdir -p /app/logs /tmp/chrome \
    && chown -R botuser:botuser /app /tmp/chrome

# Переключаемся на пользователя botuser
USER botuser

# Создаем скрипт для запуска
RUN echo '#!/bin/bash\n\
# Ждем немного для стабилизации системы\n\
sleep 2\n\
\n\
# Проверяем наличие переменных окружения\n\
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then\n\
    echo "❌ TELEGRAM_BOT_TOKEN не установлен"\n\
    exit 1\n\
fi\n\
\n\
if [ -z "$CHATGPT_EMAIL" ] || [ -z "$CHATGPT_PASSWORD" ]; then\n\
    echo "❌ CHATGPT_EMAIL или CHATGPT_PASSWORD не установлены"\n\
    exit 1\n\
fi\n\
\n\
echo "🚀 Запуск Telegram ChatGPT Bot..."\n\
echo "📱 Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."\n\
echo "📧 ChatGPT Email: $CHATGPT_EMAIL"\n\
echo "🔧 Headless Mode: ${HEADLESS_MODE:-true}"\n\
echo "⏱️ Browser Timeout: ${BROWSER_TIMEOUT:-30}s"\n\
\n\
# Запускаем бота\n\
exec python telegram_bot.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Открываем порт (если понадобится для веб-интерфейса)
EXPOSE 8080

# Устанавливаем точку входа
ENTRYPOINT ["/app/start.sh"] 