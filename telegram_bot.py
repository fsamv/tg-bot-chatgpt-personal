import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from chatgpt_client import ChatGPTClient

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chatgpt_email = os.getenv('CHATGPT_EMAIL')
        self.chatgpt_password = os.getenv('CHATGPT_PASSWORD')
        self.headless_mode = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', '30'))
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        if not self.chatgpt_email or not self.chatgpt_password:
            raise ValueError("CHATGPT_EMAIL и CHATGPT_PASSWORD должны быть указаны в переменных окружения")
        
        self.chatgpt_client = None
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = """
🤖 Привет! Я бот, который поможет вам общаться с ChatGPT.

📝 Просто отправьте мне любое сообщение, и я передам его в ChatGPT, а затем отправлю вам ответ.

💡 Примеры использования:
• "Расскажи о Python"
• "Напиши стихотворение о весне"
• "Объясни квантовую физику простыми словами"

⚠️ Обратите внимание: ответы могут занимать некоторое время, так как я обрабатываю запросы через веб-интерфейс ChatGPT.

Используйте /help для получения справки.
        """
        await update.message.reply_text(welcome_message)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = """
📚 Справка по использованию бота:

🔹 Просто отправьте текстовое сообщение, и я передам его в ChatGPT
🔹 Дождитесь ответа (это может занять 10-30 секунд)
🔹 Получите ответ от ChatGPT

📋 Доступные команды:
/start - Начать работу с ботом
/help - Показать эту справку
/status - Проверить статус подключения к ChatGPT

⚠️ Ограничения:
• Бот работает только с текстовыми сообщениями
• Не поддерживает изображения, файлы или голосовые сообщения
• Ответы могут быть ограничены тарифом Free в ChatGPT

🔄 Если бот не отвечает, попробуйте команду /status для проверки подключения.
        """
        await update.message.reply_text(help_message)
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            if self.chatgpt_client and self.chatgpt_client.driver:
                await update.message.reply_text("✅ Бот подключен к ChatGPT и готов к работе!")
            else:
                await update.message.reply_text("❌ Бот не подключен к ChatGPT. Попробуйте отправить сообщение для автоматического подключения.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при проверке статуса: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Получено сообщение от пользователя {user_id}: {user_message[:50]}...")
        
        # Отправляем сообщение о том, что обрабатываем запрос
        processing_message = await update.message.reply_text("🤔 Обрабатываю ваш запрос...")
        
        try:
            # Инициализируем ChatGPT клиент, если он еще не создан
            if not self.chatgpt_client:
                await update.message.reply_text("🔗 Подключаюсь к ChatGPT...")
                self.chatgpt_client = ChatGPTClient(
                    email=self.chatgpt_email,
                    password=self.chatgpt_password,
                    headless=self.headless_mode,
                    timeout=self.browser_timeout
                )
                
                # Настраиваем драйвер и входим в систему
                self.chatgpt_client.setup_driver()
                if not self.chatgpt_client.login():
                    await processing_message.edit_text("❌ Не удалось войти в ChatGPT. Проверьте логин и пароль.")
                    return
            
            # Отправляем сообщение в ChatGPT
            await processing_message.edit_text("💬 Отправляю запрос в ChatGPT...")
            response = self.chatgpt_client.send_message(user_message)
            
            # Отправляем ответ пользователю
            if response:
                # Разбиваем длинные ответы на части (Telegram ограничение 4096 символов)
                if len(response) > 4000:
                    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await processing_message.edit_text(chunk)
                        else:
                            await update.message.reply_text(chunk)
                else:
                    await processing_message.edit_text(response)
            else:
                await processing_message.edit_text("❌ Не удалось получить ответ от ChatGPT")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await processing_message.edit_text(f"❌ Произошла ошибка: {str(e)}")
            
            # Пытаемся переподключиться к ChatGPT
            try:
                if self.chatgpt_client:
                    self.chatgpt_client.close()
                self.chatgpt_client = None
            except:
                pass
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Ошибка в боте: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Произошла ошибка в работе бота. Попробуйте позже.")
    
    def run(self):
        """Запуск бота"""
        try:
            # Создаем приложение
            self.application = Application.builder().token(self.token).build()
            
            # Добавляем обработчики
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Добавляем обработчик ошибок
            self.application.add_error_handler(self.error_handler)
            
            logger.info("Бот запущен...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            # Закрываем браузер при завершении
            if self.chatgpt_client:
                self.chatgpt_client.close()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run() 