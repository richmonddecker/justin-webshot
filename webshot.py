import argparse
import os
import sys
import boto3
import botocore
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

def loadUrl(driver, url):
    print(f"Fetching url {url} ...")
    driver.get(url)

def saveScreenshot(driver, out, id=""):
    output = out + str(id)
    driver.save_screenshot(output)
    print(f"Saved screenshot at {output}")

def closeDriver(driver):
    driver.close()
    print("Closed driver")

def writeToBucket(file_name, bucket_name):
    try:
        print("Looking for [webshot] section in AWS credentials file...")
        session = boto3.Session(profile_name="webshot")
    except botocore.exceptions.ProfileNotFound:
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

def analyzePage(driver):
    total_height = driver.execute_script("return document.body.scrollHeight;")
    window_size = driver.get_window_size()
    inner_height = driver.execute_script("return window.innerHeight")
    height_diff = window_size.height - inner_height

    full_pages = total_height // inner_height
    leftover = total_height - full_pages * inner_height

    ### TODO::: THIS PART!!!!
    for i in range(full_pages):
        driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return 


def setupArgs():
    parser = argparse.ArgumentParser(description="Screenshot a url's webpage.")
    parser.add_argument("url", type=str,
                        help="The web url to screenshot")
    parser.add_argument("out", type=str, nargs="?", default="screenshot.png",
                        help="The output image file name")
    parser.add_argument("-b", "--bucket", type=str, default="",
                        help="The name of the s3 bucket to upload to")
    parser.add_argument("-f", "--full", action="store_true",
                        help="Whether to capture the whole webpage")
    return parser.parse_args()


if __name__ == "__main__":
    args = setupArgs()
    driver = setupDriver()

    loadUrl(driver, args.url)
    saveScreenshot(driver, args.out)
    closeDriver(driver)
    if args.bucket:
        writeToBucket(args.out, args.bucket)


