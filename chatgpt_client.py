import time
import pickle
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class ChatGPTBrowser:
    def __init__(self, email, password, headless=False, cookie_path="cookies.pkl"):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.wait = None
        self.cookie_path = cookie_path
        self.history = []

    def start(self):
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
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 60)

    def save_cookies(self):
        with open(self.cookie_path, "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_cookies(self):
        if not os.path.exists(self.cookie_path):
            return False
        with open(self.cookie_path, "rb") as f:
            cookies = pickle.load(f)
        self.driver.get("https://chat.openai.com")
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        return True

    def login(self):
        self.driver.get("https://chat.openai.com")
        time.sleep(2)

        if self.load_cookies():
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                print("✅ Вход через сохраненные cookies.")
                return True
            except:
                print("⚠️ Cookies устарели, пробуем войти вручную...")

        self.driver.get("https://chat.openai.com/auth/login")
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))).click()

        print("🟡 Вводим email...")
        email_input = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.slow_typing(email_input, self.email)
        email_input.send_keys(Keys.ENTER)

        print("🟡 Вводим пароль...")
        password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        self.slow_typing(password_input, self.password)
        password_input.send_keys(Keys.ENTER)

        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            print("✅ Успешный вход!")
            self.save_cookies()
            return True
        except Exception as e:
            print("❌ Ошибка при входе:", e)
            return False

    def slow_typing(self, element, text, delay=0.05):
        for char in text:
            element.send_keys(char)
            time.sleep(delay)

    def send_message(self, text):
        try:
            textarea = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            textarea.click()
            self.slow_typing(textarea, text)
            textarea.send_keys(Keys.ENTER)

            print("⌛ Ожидание ответа...")
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid^='conversation-turn'] .markdown"))
            )
            time.sleep(2)

            answers = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='conversation-turn'] .markdown")
            answer = answers[-1].text.strip() if answers else "[Пустой ответ]"

            self.history.append({"prompt": text, "response": answer})
            return answer
        except Exception as e:
            print("❌ Ошибка при отправке:", e)
            return "[Ошибка при получении ответа]"

    def close(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Браузер закрыт")

    def export_history(self, filename="chat_history.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i, msg in enumerate(self.history, 1):
                f.write(f"[{i}] Вопрос: {msg['prompt']}\nОтвет: {msg['response']}\n\n")
        print(f"💾 История сохранена в {filename}")
