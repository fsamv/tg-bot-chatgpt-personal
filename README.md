# Telegram ChatGPT Bot

🤖 Telegram бот для взаимодействия с ChatGPT через веб-интерфейс. Бот принимает текстовые сообщения от пользователей, отправляет их в ChatGPT и возвращает ответы обратно в Telegram.

## 🚀 Возможности

- ✅ Автоматический вход в ChatGPT с вашими учетными данными
- ✅ Обработка текстовых сообщений через Telegram
- ✅ Получение ответов от ChatGPT в реальном времени
- ✅ Поддержка длинных ответов (разбивка на части)
- ✅ Обработка ошибок и автоматическое переподключение
- ✅ Работа в headless режиме (без GUI)
- ✅ Подробное логирование

## 📋 Требования

- Python 3.8+
- Google Chrome или Chromium
- Учетная запись ChatGPT (Free тариф)
- Telegram Bot Token

## 🛠️ Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd tg-bot-chatgpt-personal
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Скопируйте файл конфигурации:
```bash
cp config.env.example .env
```

Отредактируйте файл `.env` и укажите ваши данные:
```env
# Telegram Bot Token (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# ChatGPT credentials
CHATGPT_EMAIL=your_chatgpt_email@example.com
CHATGPT_PASSWORD=your_chatgpt_password

# Server settings
HEADLESS_MODE=true
BROWSER_TIMEOUT=30
```

### 4. Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## 🚀 Запуск

### Локальный запуск
```bash
python telegram_bot.py
```

### Запуск на сервере (рекомендуется)
```bash
# Установка screen для фонового запуска
sudo apt-get install screen

# Создание новой сессии
screen -S telegram-bot

# Запуск бота
python telegram_bot.py

# Отключение от сессии (Ctrl+A, затем D)
# Для подключения к сессии: screen -r telegram-bot
```

### Запуск через systemd (для Linux серверов)

Создайте файл `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram ChatGPT Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/bot
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 📱 Использование

### Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/status` - Проверить статус подключения к ChatGPT

### Отправка сообщений

Просто отправьте любое текстовое сообщение боту, и он:
1. Подключится к ChatGPT (если еще не подключен)
2. Отправит ваше сообщение
3. Дождется ответа
4. Отправит ответ обратно в Telegram

## ⚙️ Настройки

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен вашего Telegram бота | - |
| `CHATGPT_EMAIL` | Email для входа в ChatGPT | - |
| `CHATGPT_PASSWORD` | Пароль для входа в ChatGPT | - |
| `HEADLESS_MODE` | Запуск браузера без GUI | `true` |
| `BROWSER_TIMEOUT` | Таймаут ожидания элементов (сек) | `30` |

### Настройка для продакшена

1. **Безопасность**: Никогда не коммитьте файл `.env` в репозиторий
2. **Логирование**: Настройте ротацию логов
3. **Мониторинг**: Используйте systemd или supervisor для автоматического перезапуска
4. **Обновления**: Регулярно обновляйте зависимости

## 🔧 Устранение неполадок

### Частые проблемы

1. **"Не удалось войти в ChatGPT"**
   - Проверьте правильность email и пароля
   - Убедитесь, что учетная запись активна
   - Попробуйте войти вручную в браузере

2. **"Таймаут при отправке сообщения"**
   - Увеличьте `BROWSER_TIMEOUT` в настройках
   - Проверьте стабильность интернет-соединения
   - Попробуйте перезапустить бота

3. **"Chrome driver не найден"**
   - Убедитесь, что Chrome установлен
   - Попробуйте обновить Chrome
   - Проверьте права доступа

4. **"Бот не отвечает"**
   - Проверьте логи: `tail -f bot.log`
   - Используйте команду `/status`
   - Перезапустите бота

### Логирование

Бот ведет подробные логи. Для просмотра:
```bash
# В реальном времени
tail -f bot.log

# Последние 100 строк
tail -n 100 bot.log
```

## 📝 Ограничения

- Работает только с текстовыми сообщениями
- Не поддерживает изображения, файлы или голосовые сообщения
- Ответы ограничены тарифом Free в ChatGPT
- Требует стабильное интернет-соединение
- Может работать медленнее при высокой нагрузке

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для подробностей.

## ⚠️ Отказ от ответственности

Этот бот использует веб-интерфейс ChatGPT и может перестать работать при изменениях в интерфейсе. Используйте на свой страх и риск.

## 🆘 Поддержка

Если у вас возникли проблемы:
1. Проверьте раздел "Устранение неполадок"
2. Просмотрите логи бота
3. Создайте Issue в репозитории с подробным описанием проблемы 