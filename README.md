# justin-webshot
A simple python CLI for screenshotting a webpage

** For instructions on installing and using this script, see bottom of file **

This is a command line interface to fulfill three main goals.
1. Given a URL, save a screenshot of the web page at that URL.
2. Upload the saved image file to a specified AWS S3 bucket.
3. If selected, save the WHOLE web page instead of just the top rendered screen.

To accomplish 1, I use selenium webdriver, and a package called webdriverdownloader.
The webdriverdownloader will check if the driver exists at the expected filepath.
If not, it will automatically download a Chrome webdriver to this filepath in ~/bin/chromedriver
This prevents the driver from having to be downloaded on each repeated call of the code.
Then, this driver is used to render the webpage, and to save the screenshot.

To accomplish 2, we use the boto3 library to create a Session. This Session will check the user's
AWS credentials file (default at ~/.aws/credentials) to see if a user-id and secret-key are defined.
If so, it will be able to use these credentials to upload the image to the given bucket.

To accomplish 3, we use the webdriver to scan through the whole webpage and take a screenshot at each section.
We can get the total height of the webpage, and also the browser view height (window.innerHeight). With this, we
can determine the number of full screenshots to take, scrolling down a full window height each time. Then, there will
almost always be a last smaller section to capture at the end. To get just the right size here, we shrink the window
height and take the last screenshot. All these screenshots are stored in a temporary working directory. At the end of the
process, we simply use opencv to vertically stitch these screenshots together into the one final output file.

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

** Areas for Improvement **

The error handling in this code can definitely be improved. With all these external libraries and web IO, there are
many many types of errors/exceptions that can occur. I handled some explicitly, but some I sort of ignored and some I
just caught with a basic "catch Exception as e". In general, this is not great because errors/exceptions should usually
be handled explicitly based on type. In this case, a programming challenge, it's not worth figuring out and doing all,
so I'll just mention it here.

In certain situations of bad internet connections, the code can get stuck for a very long time, trying to download from/upload to the internet. It would be ideal to program in a timeout feature, so that the code stops trying after maybe 20 seconds (instead of failing after 1 minute).

Also, I grouped all this module's functionality into functions, which much be passed in a driver each time. It could be
useful to group this functionality within a class, and store things like the driver and the file names as class attributes.
This way, all member functions would have access to this information, and the system would sort of track its state as it
moves along. However, this method also has its own drawbacks, such as being less flexible for outside use or individual
calling of functions.

** Instructions for Setup and Usage **
1. Clone the repo: git clone https://github.com/richmonddecker/justin-webshot
2. Enter the directory: cd justin-webshot
3. Create virtual environment: python -m venv ws-env
4. Source the virtual environment: source ws-env/bin/activate
5. Install packages: pip install -r requirements.txt
6. If you want to use the option to install to S3 bucket, set-up your credentials
  - In your file ~/.aws/credentials, there must be either a [default] or [webshot] section.
  - In this section, you must define aws_access_key_id and aws_secret_access_key.
  - These credentials must give you permission to upload to the desired bucket name(s) that you choose when running the script.
7. Run the script: python webshot.py url [out] [-b BUCKET] [-f]
  - [out] is an optional output file name. Default is "screenshot"
  - Include -b BUCKET (or --bucket=BUCKET) if you also want to upload the output image to the s3 bucket BUCKET.
  - Include -f (or --full) if you want to screenshot the full webpage content, not just the top window display.
8. Find your image file in ./[out].png, and in your S3 bucket BUCKET if selected.
