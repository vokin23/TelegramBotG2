import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def make_screenshot(message_link, message_id, sender_username):
    os.makedirs(sender_username, exist_ok=True)

    options = Options()
    options.add_argument("--start-fullscreen")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.get(message_link)

    # Ждем, пока элемент с классом "tgme_body_wrap" появится на странице
    wait = WebDriverWait(driver, 0)
    element_del = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_background_wrap")))
    element_del_js = driver.execute_script("return arguments[0];", element_del)
    driver.execute_script("arguments[0].remove();", element_del_js)

    element_del = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_page_widget_actions_wrap")))
    element_del_js = driver.execute_script("return arguments[0];", element_del)
    driver.execute_script("arguments[0].remove();", element_del_js)

    # element_del = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_widget_message_user")))
    # element_del_js = driver.execute_script("return arguments[0];", element_del)
    # driver.execute_script("arguments[0].remove();", element_del_js)

    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_page_widget_wrap")))

    # Делаем скриншот элемента
    element_screenshot = element.screenshot_as_png

    # Сохраняем скриншот
    with open(f"{sender_username}/{message_id}_tgme_page_widget_wrap.png", "wb") as f:
        f.write(element_screenshot)

    driver.quit()