import time
import logging
import random
import pickle
import os
import subprocess
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class ChatGPTClient:
    def __init__(self, email, password, headless=False, timeout=30, cookie_path="cookies.pkl"):
        self.email = email
        self.password = password
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.cookie_path = cookie_path
        self.history = []
        self.logger = logging.getLogger(__name__)

    def _find_chromedriver(self):
        """Поиск chromedriver с несколькими методами"""
        # Метод 1: Проверяем системный chromedriver
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/snap/bin/chromedriver",
            shutil.which("chromedriver")
        ]
        
        for path in chromedriver_paths:
            if path and os.path.exists(path):
                self.logger.info(f"Найден chromedriver: {path}")
                return path
        
        # Метод 2: Пытаемся использовать webdriver-manager
        try:
            self.logger.info("Пытаемся загрузить chromedriver через webdriver-manager...")
            driver_path = ChromeDriverManager().install()
            if driver_path and os.path.exists(driver_path):
                self.logger.info(f"ChromeDriver загружен: {driver_path}")
                return driver_path
            else:
                self.logger.warning("ChromeDriverManager вернул неверный путь")
        except Exception as e:
            self.logger.warning(f"Ошибка при загрузке через webdriver-manager: {e}")
        
        # Метод 3: Пытаемся найти chromedriver в PATH
        try:
            result = subprocess.run(['which', 'chromedriver'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                path = result.stdout.strip()
                if os.path.exists(path):
                    self.logger.info(f"Найден chromedriver в PATH: {path}")
                    return path
        except Exception as e:
            self.logger.warning(f"Ошибка при поиске chromedriver в PATH: {e}")
        
        return None

    def _check_chromium_installation(self):
        """Проверка установки Chromium"""
        chromium_paths = [
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            shutil.which("chromium-browser"),
            shutil.which("chromium")
        ]
        
        for path in chromium_paths:
            if path and os.path.exists(path):
                self.logger.info(f"Найден Chromium: {path}")
                return True
        
        # Проверяем через команду
        try:
            result = subprocess.run(['which', 'chromium-browser'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info(f"Найден Chromium в PATH: {result.stdout.strip()}")
                return True
        except Exception:
            pass
        
        return False

    def setup_driver(self):
        """Настройка Chrome/Chromium WebDriver"""
        # Проверяем установку Chromium
        if not self._check_chromium_installation():
            raise Exception("Chromium не найден. Установите Chromium: sudo apt install chromium-browser")
        
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Поиск chromedriver
        chromedriver_path = self._find_chromedriver()
        if not chromedriver_path:
            raise Exception("Не удалось найти chromedriver. Установите chromedriver: sudo apt install chromium-chromedriver")
        
        try:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.logger.info("Chrome/Chromium WebDriver успешно запущен")
        except Exception as e:
            self.logger.error(f"Ошибка запуска Chrome: {e}")
            # Попробуем запустить без Service
            try:
                self.logger.info("Пробуем запустить без Service...")
                self.driver = webdriver.Chrome(options=options)
                self.logger.info("Chrome/Chromium WebDriver запущен без Service")
            except Exception as e2:
                self.logger.error(f"Ошибка запуска Chrome без Service: {e2}")
                raise Exception(f"Не удалось запустить Chrome/Chromium. Убедитесь, что версии Chromium и chromedriver совместимы: {e2}")
        
        self.wait = WebDriverWait(self.driver, self.timeout)
        
        # Отключаем navigator.webdriver через JS
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

    def save_cookies(self):
        """Сохранение cookies"""
        try:
            with open(self.cookie_path, "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            self.logger.info("Cookies сохранены")
        except Exception as e:
            self.logger.warning(f"Ошибка при сохранении cookies: {e}")

    def load_cookies(self):
        """Загрузка cookies"""
        if not os.path.exists(self.cookie_path):
            return False
        try:
            with open(self.cookie_path, "rb") as f:
                cookies = pickle.load(f)
            self.driver.get("https://chat.openai.com")
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass
            self.driver.refresh()
            self.logger.info("Cookies загружены")
            return True
        except Exception as e:
            self.logger.warning(f"Ошибка при загрузке cookies: {e}")
            return False

    def login(self):
        """Вход в ChatGPT"""
        try:
            self.logger.info("Открываем ChatGPT...")
            self.driver.get("https://chat.openai.com")
            time.sleep(random.uniform(1.5, 2.5))

            # Пытаемся войти через cookies
            if self.load_cookies():
                try:
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                    self.logger.info("✅ Вход через сохраненные cookies")
                    return True
                except:
                    self.logger.info("⚠️ Cookies устарели, пробуем войти вручную...")

            # Ручной вход
            self.driver.get("https://chat.openai.com/auth/login")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_button.click()
            time.sleep(random.uniform(1.0, 2.0))

            # Вводим email
            self.logger.info("Вводим email...")
            email_input = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            email_input.clear()
            self.slow_typing(email_input, self.email)
            time.sleep(random.uniform(0.5, 1.0))
            email_input.send_keys(Keys.ENTER)
            time.sleep(random.uniform(1.0, 2.0))

            # Вводим пароль
            self.logger.info("Вводим пароль...")
            password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input.clear()
            self.slow_typing(password_input, self.password)
            time.sleep(random.uniform(0.5, 1.0))
            password_input.send_keys(Keys.ENTER)

            # Ждем загрузки чата
            self.logger.info("Ожидаем загрузки чата...")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            
            self.logger.info("✅ Успешный вход в ChatGPT")
            self.save_cookies()
            return True
            
        except TimeoutException as e:
            self.logger.error(f"Таймаут при входе: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при входе: {e}")
            return False

    def slow_typing(self, element, text, min_delay=0.07, max_delay=0.18):
        """Медленный ввод текста для эмуляции пользователя"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    def send_message(self, message):
        """Отправка сообщения в ChatGPT и получение ответа"""
        try:
            # Находим поле ввода
            textarea = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            textarea.click()
            textarea.clear()
            
            # Вводим сообщение медленно
            self.slow_typing(textarea, message)
            time.sleep(random.uniform(0.2, 0.5))
            textarea.send_keys(Keys.ENTER)

            # Ждем начала генерации ответа
            self.logger.info("Ожидаем ответ от ChatGPT...")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid^='conversation-turn'] .markdown"))
            )
            
            # Ждем завершения генерации
            time.sleep(2)

            # Получаем ответ
            answers = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='conversation-turn'] .markdown")
            if answers:
                response = answers[-1].text.strip()
                self.logger.info("Ответ получен")
                self.history.append({"prompt": message, "response": response})
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

    def export_history(self, filename="chat_history.txt"):
        """Экспорт истории чата"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                for i, msg in enumerate(self.history, 1):
                    f.write(f"[{i}] Вопрос: {msg['prompt']}\nОтвет: {msg['response']}\n\n")
            self.logger.info(f"История сохранена в {filename}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении истории: {e}")
