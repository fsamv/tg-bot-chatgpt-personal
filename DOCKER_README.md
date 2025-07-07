# 🐳 Docker развертывание Telegram ChatGPT Bot

Этот документ описывает, как развернуть Telegram бота с ChatGPT в Docker контейнере.

## 📋 Требования

- Docker Engine 20.10+
- Docker Compose 2.0+
- Минимум 2GB RAM
- 10GB свободного места на диске

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd tg-bot-chatgpt-personal

# Создайте файл конфигурации
cp config.env.example .env

# Отредактируйте .env файл
nano .env
```

### 2. Запуск с помощью скрипта

```bash
# Сделайте скрипт исполняемым
chmod +x docker-run.sh

# Запустите бота
./docker-run.sh
```

### 3. Ручной запуск

```bash
# Сборка и запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f
```

## 📁 Структура файлов

```
├── Dockerfile                 # Основной Docker образ
├── docker-compose.yml         # Конфигурация для разработки
├── docker-compose.prod.yml    # Конфигурация для продакшена
├── .dockerignore             # Исключения для Docker
├── docker-run.sh             # Скрипт для запуска
└── DOCKER_README.md          # Эта документация
```

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` на основе `config.env.example`:

```env
# Telegram Bot Token (обязательно)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# ChatGPT credentials (обязательно)
CHATGPT_EMAIL=your_chatgpt_email@example.com
CHATGPT_PASSWORD=your_chatgpt_password

# Настройки браузера (опционально)
HEADLESS_MODE=true
BROWSER_TIMEOUT=30
```

### Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env`

## 🐳 Команды Docker

### Основные команды

```bash
# Сборка образа
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Запуск с выводом логов
docker-compose up

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Управление контейнером

```bash
# Войти в контейнер
docker-compose exec telegram-chatgpt-bot bash

# Просмотр логов в реальном времени
docker-compose logs -f --tail=100

# Остановка и удаление
docker-compose down -v

# Очистка образов
docker system prune -f
```

## 🔧 Использование скрипта docker-run.sh

Скрипт автоматизирует процесс развертывания:

```bash
# Запуск бота
./docker-run.sh

# Остановка
./docker-run.sh stop

# Перезапуск
./docker-run.sh restart

# Просмотр логов
./docker-run.sh logs

# Статус
./docker-run.sh status

# Очистка
./docker-run.sh clean

# Справка
./docker-run.sh help
```

## 🏭 Продакшен развертывание

### Использование production конфигурации

```bash
# Запуск с production настройками
docker-compose -f docker-compose.prod.yml up -d

# С nginx (опционально)
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### Настройки для продакшена

- Ограниченные ресурсы (1GB RAM, 0.5 CPU)
- Улучшенная безопасность
- Ротация логов
- Health checks
- Автоматический перезапуск

## 📊 Мониторинг

### Просмотр логов

```bash
# Логи контейнера
docker-compose logs -f

# Логи с ограничением строк
docker-compose logs --tail=50

# Логи с временными метками
docker-compose logs -t

# Логи в файл
docker-compose logs > bot.log
```

### Проверка здоровья

```bash
# Статус контейнера
docker-compose ps

# Детальная информация
docker inspect telegram-chatgpt-bot

# Использование ресурсов
docker stats telegram-chatgpt-bot
```

### Логи в файловой системе

Логи сохраняются в директории `./logs`:

```bash
# Просмотр логов
tail -f logs/bot.log

# Поиск ошибок
grep ERROR logs/bot.log
```

## 🔒 Безопасность

### Рекомендации

1. **Не коммитьте `.env` файл**
2. **Используйте секреты Docker** для продакшена
3. **Ограничивайте ресурсы** контейнера
4. **Регулярно обновляйте** базовый образ
5. **Мониторьте логи** на предмет подозрительной активности

### Использование Docker Secrets

```bash
# Создание секретов
echo "your_bot_token" | docker secret create telegram_bot_token -
echo "your_email" | docker secret create chatgpt_email -
echo "your_password" | docker secret create chatgpt_password -

# Использование в docker-compose
secrets:
  - telegram_bot_token
  - chatgpt_email
  - chatgpt_password
```

## 🚨 Устранение неполадок

### Частые проблемы

1. **Контейнер не запускается**
   ```bash
   # Проверьте логи
   docker-compose logs
   
   # Проверьте переменные окружения
   docker-compose config
   ```

2. **Chrome не запускается**
   ```bash
   # Проверьте права доступа
   docker-compose exec telegram-chatgpt-bot ls -la /tmp/chrome
   
   # Пересоберите образ
   docker-compose build --no-cache
   ```

3. **Недостаточно памяти**
   ```bash
   # Увеличьте лимиты в docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 2G
   ```

4. **Проблемы с сетью**
   ```bash
   # Проверьте сеть
   docker network ls
   
   # Пересоздайте сеть
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

### Отладка

```bash
# Войти в контейнер для отладки
docker-compose exec telegram-chatgpt-bot bash

# Проверить процессы
ps aux

# Проверить переменные окружения
env | grep -E "(TELEGRAM|CHATGPT)"

# Проверить логи Python
tail -f /app/logs/bot.log
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Запуск нескольких экземпляров
docker-compose up -d --scale telegram-chatgpt-bot=3
```

### Использование Docker Swarm

```bash
# Инициализация swarm
docker swarm init

# Развертывание стека
docker stack deploy -c docker-compose.yml telegram-bot
```

## 🔄 Обновления

### Обновление бота

```bash
# Остановка
docker-compose down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose up -d --build
```

### Обновление базового образа

```bash
# Принудительная пересборка
docker-compose build --no-cache

# Обновление зависимостей
docker-compose exec telegram-chatgpt-bot pip install -r requirements.txt --upgrade
```

## 📝 Лучшие практики

1. **Используйте теги образов** для версионирования
2. **Настройте мониторинг** и алерты
3. **Регулярно делайте бэкапы** конфигурации
4. **Тестируйте обновления** в staging окружении
5. **Документируйте изменения** в конфигурации

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте раздел "Устранение неполадок"
2. Просмотрите логи контейнера
3. Проверьте переменные окружения
4. Создайте Issue с подробным описанием проблемы

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
- [Selenium Docker](https://github.com/SeleniumHQ/docker-selenium) 