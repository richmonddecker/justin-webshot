import os
import sys
import boto3
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

def writeToBucket(file_name, bucket_name):
    try:
        print("Looking for [webshot] section in AWS credentials file...")
        session = boto3.Session(profile_name="webshot")
    except botocore.exceptions.ProfileNotFound(e):
        try:
            print("Using [default] credentials in AWS credentials file...")
            session = boto3.Session(profile_name="default")
        except botocore.exceptions.ProfileNotFound:
            print("No valid AWS credentials file with [default] or [webshot].")
            return
    
    client = session.client("s3")
    print(f"Uploading {file_name} to bucket {bucket_name}...")
    try:
        client.upload_file(file_name, bucket_name, file_name)
        print("Uploaded successfully to bucket.")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    screenshot = "screenshot.png"
    driver = setupDriver()
    url = sys.argv[1]
    driver.get(url)
    print(f"Fetching url {url} ...")
    driver.save_screenshot(screenshot)
    print(f"Saved screenshot at {screenshot}")
    driver.close()
    print("Closed driver")

