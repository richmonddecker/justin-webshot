import os
import sys
import webdriverdownloader
from selenium import webdriver

def setupDriver():
    cdd = webdriverdownloader.ChromeDriverDownloader()
    print("Installing driver...")
    cdd.download_and_install()
    driver_path = cdd.link_path + os.sep + cdd.get_driver_filename()
    print(f"Driver installed at {driver_path}")
    print("Running driver...")
    driver = webdriver.Chrome(driver_path)
    return driver

if __name__ == "__main__":
    screenshot = "screenshot.png"
    driver = setupDriver()
    url = sys.argv[1]
    driver.get(url)
    print(f"Fetching url {url}")
    driver.save_screenshot(screenshot)
    print(f"Saved screenshot at {screenshot}")
    driver.close()
    print("Closed driver")
