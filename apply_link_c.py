from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


def get_apply_link_crypto(url):
    driver_path = 'static/chromedriver.exe'

    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    apply_link = ''

    try:
        driver.maximize_window()
        driver.get(url)

        time.sleep(3)

        a_tag = driver.find_element(By.XPATH, '//a[contains(@class, "inline-block w-full") and contains(@class, "text-white")]')
        apply_link = a_tag.get_attribute('href')

        if a_tag:
            apply_link = a_tag.get_attribute('href')

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()

    # time.sleep(3)
    return apply_link
