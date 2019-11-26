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

def saveScreenshot(driver, url, out):
    driver.get(url)
    print(f"Fetching url {url} ...")
    driver.save_screenshot(out)
    print(f"Saved screenshot at {out}")
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

    saveScreenshot(driver, args.url, args.out)
    if args.bucket:
        writeToBucket(args.out, args.bucket)


