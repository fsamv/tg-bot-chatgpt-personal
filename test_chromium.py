#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики проблем с Chromium и chromedriver
"""

import os
import sys
import subprocess
import shutil
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_command(command, description):
    """Проверка наличия команды"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"✅ {description}: {version}")
            return True, version
        else:
            logger.error(f"❌ {description}: команда вернула код {result.returncode}")
            return False, None
    except FileNotFoundError:
        logger.error(f"❌ {description}: команда не найдена")
        return False, None
    except Exception as e:
        logger.error(f"❌ {description}: ошибка - {e}")
        return False, None

def check_path(path, description):
    """Проверка наличия файла по пути"""
    if os.path.exists(path):
        logger.info(f"✅ {description}: {path}")
        return True
    else:
        logger.error(f"❌ {description}: файл не найден")
        return False

def main():
    print("🔍 Диагностика Chromium и chromedriver")
    print("=" * 50)
    
    # Проверка Python и зависимостей
    print("\n📦 Проверка Python и зависимостей:")
    logger.info(f"Python версия: {sys.version}")
    
    try:
        import selenium
        logger.info(f"Selenium версия: {selenium.__version__}")
    except ImportError:
        logger.error("❌ Selenium не установлен")
        return
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        logger.info("✅ webdriver-manager установлен")
    except ImportError:
        logger.error("❌ webdriver-manager не установлен")
        return
    
    # Проверка Chromium
    print("\n🌐 Проверка Chromium:")
    chromium_found = False
    
    # Проверяем различные команды
    chromium_commands = [
        ('chromium', 'Chromium'),
        ('chromium-browser', 'Chromium Browser'),
        ('google-chrome', 'Google Chrome'),
        ('google-chrome-stable', 'Google Chrome Stable')
    ]
    
    for cmd, desc in chromium_commands:
        found, version = check_command(cmd, desc)
        if found:
            chromium_found = True
    
    # Проверяем snap
    try:
        result = subprocess.run(['snap', 'list', 'chromium'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'chromium' in result.stdout:
            logger.info("✅ Chromium установлен через snap")
            chromium_found = True
    except:
        pass
    
    # Проверяем пути
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/snap/bin/chromium',
        '/usr/bin/google-chrome-stable'
    ]
    
    for path in chromium_paths:
        if check_path(path, f"Chromium по пути {path}"):
            chromium_found = True
    
    if not chromium_found:
        logger.error("❌ Chromium не найден нигде!")
        print("\n💡 Рекомендации:")
        print("   sudo apt install chromium-browser chromium-chromedriver")
        print("   или")
        print("   sudo snap install chromium")
        return
    
    # Проверка chromedriver
    print("\n🚗 Проверка chromedriver:")
    chromedriver_found = False
    
    # Проверяем команду
    found, version = check_command('chromedriver', 'chromedriver')
    if found:
        chromedriver_found = True
    
    # Проверяем пути
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/snap/bin/chromedriver'
    ]
    
    for path in chromedriver_paths:
        if check_path(path, f"chromedriver по пути {path}"):
            chromedriver_found = True
    
    # Проверяем через which
    which_path = shutil.which('chromedriver')
    if which_path:
        logger.info(f"✅ chromedriver найден через which: {which_path}")
        chromedriver_found = True
    
    if not chromedriver_found:
        logger.error("❌ chromedriver не найден!")
        print("\n💡 Рекомендации:")
        print("   sudo apt install chromium-chromedriver")
        print("   или используйте webdriver-manager")
    
    # Тест webdriver-manager
    print("\n🔧 Тест webdriver-manager:")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        logger.info("Пытаемся загрузить chromedriver через webdriver-manager...")
        driver_path = ChromeDriverManager().install()
        if driver_path and os.path.exists(driver_path):
            logger.info(f"✅ ChromeDriver загружен: {driver_path}")
        else:
            logger.error("❌ ChromeDriverManager вернул неверный путь")
    except Exception as e:
        logger.error(f"❌ Ошибка webdriver-manager: {e}")
    
    # Тест Selenium
    print("\n🧪 Тест Selenium:")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        logger.info("Пытаемся запустить Chrome через Selenium...")
        
        # Пробуем с Service
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome запущен с Service")
            driver.quit()
        except Exception as e:
            logger.warning(f"Ошибка с Service: {e}")
            
            # Пробуем без Service
            try:
                driver = webdriver.Chrome(options=chrome_options)
                logger.info("✅ Chrome запущен без Service")
                driver.quit()
            except Exception as e2:
                logger.error(f"Ошибка без Service: {e2}")
                
    except Exception as e:
        logger.error(f"❌ Ошибка теста Selenium: {e}")
    
    print("\n📋 Резюме:")
    if chromium_found and chromedriver_found:
        print("✅ Chromium и chromedriver найдены")
        print("💡 Попробуйте запустить бота: python telegram_bot.py")
    else:
        print("❌ Есть проблемы с установкой")
        print("💡 Запустите setup.sh для автоматической установки")

if __name__ == "__main__":
    main() 