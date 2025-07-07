import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class ChatGPTClient:
    def __init__(self, email, password, headless=True, timeout=30):
        self.email = email
        self.password = password
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Настройка Chrome/Chromium WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Основные настройки для работы в контейнере
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Ускоряет загрузку
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Дополнительные настройки для стабильности
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Отключаем логи и расширения
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        })
        
        try:
            # Пытаемся использовать системный chromedriver (для Chromium)
            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.warning(f"Не удалось использовать системный chromedriver: {e}")
            # Fallback на webdriver-manager
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                self.logger.error(f"Не удалось инициализировать WebDriver: {e2}")
                raise
        
        self.wait = WebDriverWait(self.driver, self.timeout)
        
    def login(self):
        """Вход в ChatGPT"""
        try:
            self.logger.info("Открываем ChatGPT...")
            self.driver.get("https://chat.openai.com")
            
            # Ждем появления кнопки входа
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            )
            login_button.click()
            
            # Вводим email
            self.logger.info("Вводим email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            
            # Нажимаем Continue
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            continue_button.click()
            
            # Вводим пароль
            self.logger.info("Вводим пароль...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Нажимаем Continue для входа
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            continue_button.click()
            
            # Ждем загрузки чата
            self.logger.info("Ожидаем загрузки чата...")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))
            )
            
            self.logger.info("Успешный вход в ChatGPT")
            return True
            
        except TimeoutException as e:
            self.logger.error(f"Таймаут при входе: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при входе: {e}")
            return False
    
    def send_message(self, message):
        """Отправка сообщения в ChatGPT и получение ответа"""
        try:
            # Находим поле ввода
            textarea = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Message']"))
            )
            
            # Очищаем поле и вводим сообщение
            textarea.clear()
            textarea.send_keys(message)
            
            # Нажимаем кнопку отправки
            send_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
            )
            send_button.click()
            
            # Ждем начала генерации ответа
            self.logger.info("Ожидаем ответ от ChatGPT...")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-turn-2']"))
            )
            
            # Ждем завершения генерации (кнопка отправки снова становится активной)
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
            )
            
            # Получаем ответ
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='conversation-turn-2'] .markdown")
            if response_elements:
                response = response_elements[-1].text
                self.logger.info("Ответ получен")
                return response
            else:
                self.logger.warning("Не удалось найти ответ")
                return "Извините, не удалось получить ответ от ChatGPT"
                
        except TimeoutException as e:
            self.logger.error(f"Таймаут при отправке сообщения: {e}")
            return "Извините, произошла ошибка при получении ответа"
        except Exception as e:
            self.logger.error(f"Ошибка при отправке сообщения: {e}")
            return f"Произошла ошибка: {str(e)}"
    
    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Браузер закрыт") 