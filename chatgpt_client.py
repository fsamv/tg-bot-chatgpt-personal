import time
import logging
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class ChatGPTClient:
    def __init__(self, email, password, headless=False, timeout=30):
        self.email = email
        self.password = password
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        self.cookies_file = "chatgpt_cookies.json"
        self.session_file = "chatgpt_session.json"
        
    def setup_driver(self):
        """Настройка Chrome/Chromium WebDriver"""
        chrome_options = Options()
        
        # Headless отключен для эмуляции пользователя
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Основные настройки для работы в контейнере
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,900")
        # User-Agent как у обычного пользователя
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Отключаем автоматизацию
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # Отключаем navigator.webdriver
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Прочие настройки
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        })
        
        try:
            # Пытаемся использовать системный chromedriver (для Chromium)
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.error(f"Ошибка запуска Chrome: {e}")
            raise
        
        self.wait = WebDriverWait(self.driver, self.timeout)
        # Отключаем navigator.webdriver через JS
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        # Загружаем cookies если есть
        self._load_cookies()
        
    def _slow_type(self, element, text, min_delay=0.07, max_delay=0.18):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    def _save_cookies(self):
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f)
        self.logger.info("Cookies сохранены")

    def _load_cookies(self):
        if os.path.exists(self.cookies_file):
            self.driver.get("https://chat.openai.com")
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                    cookie['sameSite'] = 'Strict'
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass
            self.driver.refresh()
            self.logger.info("Cookies загружены")
        
    def login(self):
        """Вход в ChatGPT"""
        try:
            self.logger.info("Открываем ChatGPT...")
            self.driver.get("https://chat.openai.com")
            time.sleep(random.uniform(1.5, 2.5))
            
            # Ждем появления кнопки входа
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            )
            login_button.click()
            time.sleep(random.uniform(1.0, 2.0))
            
            # Вводим email медленно
            self.logger.info("Вводим email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.clear()
            self._slow_type(email_input, self.email)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Нажимаем Continue
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            continue_button.click()
            time.sleep(random.uniform(1.0, 2.0))
            
            # Вводим пароль медленно
            self.logger.info("Вводим пароль...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            self._slow_type(password_input, self.password)
            time.sleep(random.uniform(0.5, 1.0))
            
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
            self._save_cookies()
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
            self._slow_type(textarea, message)
            time.sleep(random.uniform(0.2, 0.5))
            
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