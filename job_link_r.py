from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


def get_job_link_remote3(url):
    driver_path = 'static/chromedriver.exe'

    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    items = []

    try:
        driver.maximize_window()
        driver.get(url)

        time.sleep(3)

        elements = driver.find_elements(By.XPATH, '//a[contains(@class, "bubble-element") and contains(@class, "Link") and contains(@class, "clickable-element")]')[4:20]
        items = [element.get_attribute('href') for element in elements]

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()

    # time.sleep(3)
    return items
