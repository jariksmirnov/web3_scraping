from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


def get_apply_link_web3(url):
    driver_path = 'static/chromedriver.exe'

    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    apply_link = ''

    try:
        driver.maximize_window()
        driver.get(url)

        time.sleep(3)

        element = driver.find_element(By.XPATH, "// div[@class =' mt-4 d-flex justify-content-center gap-3 mb-4'] // a[@ class ='my-btn my-btn-primary-maximum'][normalize-space()='Apply Now']")
        element.click()
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)

        apply_link = driver.current_url

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()

    return apply_link
