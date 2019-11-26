# justin-webshot
A simple python CLI for screenshotting a webpage

This is a command line interface to fulfill three main goals.
1. Given a URL, save a screenshot of the web page at that URL.
2. Upload the saved image file to a specified AWS S3 bucket.
3. If selected, save the WHOLE web page instead of just the top rendered screen.

To accomplish 1, I use selenium webdriver, and a package called webdriverdownloader.
The webdriverdownloader will automatically download a Chrome webdriver each time.
Although this repeated functionality is not ideal, it ensures that there is always a functioning
driver installed on the system and that it knows where this driver is located.
Then, this driver is used to render the webpage, and to save the screenshot.

To accomplish 2, we use the boto3 library to create a Session. This Session will check the user's
AWS credentials file (default at ~/.aws/credentials) to see if a user-id and secret-key are defined.
If so, it will be able to use these credentials to upload the image to the given bucket.

To accomplish 3, we...

We use argparse to parse the command line arguments, which takes the following format:

usage: webshot.py [-h] [-b BUCKET] [-f] url [out]

Screenshot a url's webpage.

positional arguments:
  url                   The web url to screenshot
  out                   The output image file name

optional arguments:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        The name of the s3 bucket to upload to
  -f, --full            Whether to capture the whole webpage
