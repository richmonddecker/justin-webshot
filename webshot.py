import argparse
import os
import shutil
import sys

import boto3
import botocore
import cv2
import webdriverdownloader
from selenium import webdriver

def setupDriver():
    """Download and setup a Chrome driver, returning this driver."""
    try:
        cdd = webdriverdownloader.ChromeDriverDownloader()
        print("Installing driver...")
        cdd.download_and_install()
        driver_path = cdd.link_path + os.sep + cdd.get_driver_filename()
        print(f"Driver installed at {driver_path}")
        print("Running driver...")
        driver = webdriver.Chrome(driver_path)
        return driver
    except Exception as e:
        print(e)
        raise RuntimeError("Couldn't set up webdriver. Are you online?")

def loadUrl(driver, url):
    """Load the url using the given driver."""
    print(f"Fetching url {url} ...")
    driver.get(url)

def saveScreenshot(driver, out, dname="", fid=""):
    """
    Save screenshot using the driver to a given output filename.
    With dir and id optional arguments, a directory will be used
    and an fid number appended at the end of the filename.
    """
    dstring = dname + "/" if dname else ""
    output = f"{dstring}{out}{fid}.png"
    driver.save_screenshot(output)
    print(f"Saved screenshot at {output}")
    return output

def closeDriver(driver):
    """Close the driver. A bit useless but included for consistency sake."""
    driver.close()
    print("Closed driver")

def writeToBucket(file_name, bucket_name):
    """
    Save the file at given file_name to the given S3 bucket on AWS.
    The user must have a valid ~/.aws/credentials file with authentication
    credentials specified in either [webshot] or [default] sections.
    """
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
        # Not good Exception handling, I know, but it's just an exercise. :)
        print(e)

def analyzePage(driver):
    """Get useful height info about the page to determine how to scroll."""
    total_height = driver.execute_script("return document.body.scrollHeight;")
    window_size = driver.get_window_size()
    inner_height = driver.execute_script("return window.innerHeight")
    height_diff = window_size["height"] - inner_height
    
    full_pages = total_height // inner_height
    leftover = total_height - full_pages * inner_height
    last_height = leftover + height_diff if leftover else 0

    # Probably better to return a namedtuple or something similar
    return full_pages, inner_height, window_size["width"], last_height

def combineImage(dir_name, out, count):
    try:
        # Read all images into a list
        images = [cv2.imread(f"{dir_name}/{out}{i}.png") for i in range(count)]
        stitched = cv2.vconcat(images)
        cv2.imwrite(f"{out}.png", stitched)
        return 
    except Exception as e:
        # Yes yes, terrible exception handling, gimme a break. :)
        print(e)


def scanPage(driver, out, full_pages, page_height, page_width, last_height):
    dir_name = "pieces"
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass
    for i in range(full_pages):
        saveScreenshot(driver, out, dir_name, i)
        scrollY = (i + 1) * page_height
        driver.execute_script(f"window.scrollTo(0, {scrollY});")

    if last_height:
        driver.set_window_size(page_width, last_height)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        saveScreenshot(driver, out, dir_name, i + 1)

    combineImage(dir_name, out, i + 1)

    try:
        # Clean up that working directory
        shutil.rmtree(dir_name)
    except Exception:
        # Eh, whatever. :)
        pass


def setupArgs():
    """
    Parse information from arguments about the url and outpit filename.
    Also have optional bucket argument and flag for saving full webpage.
    """
    parser = argparse.ArgumentParser(description="Screenshot a url's webpage.")
    parser.add_argument("url", type=str,
                        help="The web url to screenshot")
    parser.add_argument("out", type=str, nargs="?", default="screenshot",
                        help="The output image file name (without extension)")
    parser.add_argument("-b", "--bucket", type=str, default="",
                        help="The name of the s3 bucket to upload to")
    parser.add_argument("-f", "--full", action="store_true",
                        help="Whether to capture the whole webpage")
    return parser.parse_args()


if __name__ == "__main__":
    args = setupArgs()
    driver = setupDriver()

    loadUrl(driver, args.url)
    if args.full:
        scanPage(driver, args.out, *analyzePage(driver))
    else:
        saveScreenshot(driver, args.out)
    closeDriver(driver)
    if args.bucket:
        writeToBucket(f"{args.out}.png", args.bucket)


