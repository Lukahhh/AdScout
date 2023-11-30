# AdScout


# What is it?
AdScout is a side-project for automatically scraping Facebook to locate Sponsored posts. The desktop and mobile scripts will:
- Open a Chrome instance in "remote debugging" mode
- Visit Facebook.com (you must already be signed in to Facebook on the Chrome session with remote debugging enabled)
- Scroll through the news feed and identify Sponsored posts
- Take screenshots of each sponsored post
- Collect accessible data (such as profile URL, profile name, visible URL, etc)
- Store that data in a CSV file



# Environment

- MacOS 13.1 (you can run this on Windows with some adjustments, but your mileage may vary)
- Python 3.9.7
- Virtualenv for requirements.txt
- Google Chrome 119.0.6045.159
- [Chrome Driver](https://chromedriver.chromium.org/downloads/version-selection) suitable to your device and Chrome version

## Set up
- Install Python
- Install Chrome
- Install Chrome Driver
- Install requirements.txt



# Script Overview
## Desktop
This script is designed to automate the process of identifying and analyzing sponsored posts on Facebook. It uses Selenium for web automation, Pytesseract for optical character recognition (OCR), and other Python utilities for file and data handling.

### Key Components

#### Import Required Libraries
- `selenium` for web automation tasks.
- `datetime` for timestamping screenshots.
- `time` for managing delays in script execution.
- `pytesseract` and `PIL` for image processing and OCR.
- `os` and `traceback` for file operations and error handling.
- `csv` for handling CSV file operations.

#### Whitelist and Blacklist
- `whitelist`: Keywords or sources considered safe. 
- `blacklist`: Keywords or sources marked as untrusted.

#### CSV File Handling
- Function `append_to_csv` for appending data to a CSV file.

#### Path Configuration
- Set up the CSV file path for storing data.
- Configure the path to the Tesseract OCR executable.

#### Chrome WebDriver Setup
- Configure user agent for browsing (mobile/desktop).
- Initialize Selenium WebDriver with Chrome options.

#### Navigate to Facebook
- Set the browser window size.
- Open Facebook's website for scraping.

#### Initial Page Load Handling
- Explicit wait for the initial page load.
- Scroll down to load and cache posts.

#### Post Processing in a Loop
- Fetch and filter posts based on specific attributes.
- Identify posts containing the keyword "Sponsored".

#### Sponsored Post Processing
- Scroll each post into view for analysis.
- Take screenshots for OCR analysis.
- Enhance images to improve OCR accuracy.

#### OCR and Text Analysis
- Use `pytesseract` for OCR on images.
- Analyze text to detect "Sponsored" labels.

#### Extracting Information from Sponsored Posts
- Extract details like profile URL, title, visible URL, ad destination URL, and call to action.
- Classify posts based on whitelist and blacklist.
- Append extracted data to the CSV file.

#### Scrolling for More Posts
- Scroll down to load additional posts after processing.

#### Error Handling and Clean-up
- Exception handling during post processing and scrolling.
- Quit the WebDriver upon script completion or error.


## Mobile Web
This script automates the process of identifying and analyzing sponsored posts on Facebook using Selenium. It captures screenshots of sponsored posts, extracts relevant information, and stores it for further analysis.

### Key Components

#### Import Required Libraries
- `selenium`: For web automation.
- `datetime`: For timestamping screenshots.
- `time`: For managing delays.
- `pytesseract` and `PIL`: For image processing and OCR. Note: Pytesseract is no longer used for the mobile script as we use Selenium to locate Sponsored posts in the HTML.
- `os` and `traceback`: For file and error handling.
- `csv`: For CSV file operations.
- `Keys`: For keyboard interactions. Note: No longer used.

#### Whitelist and Blacklist Definitions
- `whitelist`: Keywords or sources considered safe. Note: No longer used.
- `blacklist`: Keywords or sources flagged as untrusted. Note: No longer used.
 
#### CSV File Handling
- `append_to_csv` function: Appends data to a specified CSV file.
- `csv_file_path`: File path for storing scraped data.

#### Tesseract Configuration
- Sets the path to the Tesseract OCR executable for text recognition.

#### Chrome WebDriver Setup
- Sets user agent for mobile/desktop browsing.
- Initializes Selenium WebDriver with Chrome options for remote debugging.

#### WebDriver Initialization
- Sets the path to ChromeDriver.
- Connects to an already-opened Chrome session.

#### Script Execution Flow
- Opens Facebook and waits for the initial page load.
- Performs an initial scrolling phase to load and cache posts.
- Scrolls back to the top of the page.

#### Processing Loop
- Fetches all potential posts with specific attributes.
- Filters posts containing the word "Sponsored".
- Scrolls each sponsored post into view for further processing.

#### Sponsored Post Processing
- Takes screenshots of sponsored posts.
- Attempts to extract profile title and URL using JavaScript click and navigation.
- Renames the screenshots for clarity.
- Extracts visible URLs from posts.

#### Data Extraction
- Attempts to extract various elements from sponsored posts, including profile URL, profile title, and visible URL.
- Handles exceptions and errors during extraction.

#### Data Storage
- Appends extracted data to a CSV file.
- Handles exceptions during data storage.

#### Post-Processing Navigation
- Scrolls down to load new posts.
- Handles scrolling errors.

#### Error Handling
- Catches and logs exceptions during script execution.
- Exits the WebDriver upon script completion or error.


# Running the code

1. Start Chrome in Remote Debugging Mode:

`/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_session`

 * The reason we use Chrome in Remote Debugging Mode (RDM) is because signing in via a Selenium/ChromeDriver creates a "clean slate" with no cookies or login details, requiring the username and password for the Facebook account you wish to use to be stored in plain text in the script. Earlier versions of this script made use of that

2. Sign in to Facebook on the Chrome RDM session

3. If you've set up a virtual environment, run the appropriate command to activate it:

`source myenv/bin/activate`

4. Run the appropriate script, e.g. for desktop:

`python3 desktop_script/adscout_desktop.py`

5. The script will create a new CSV file in the `/csv/` folder if it doesn't already exist. If a CSV file exists, it will amend to that file. 


# FAQ
## Why are there separate scripts for desktop and mobile?
Selenium looks specifically for certain parts of the code to identify things such as the Facebook Profile ID, call to action text, and visible URL. The underlying page code is different between Facebook mobile web and desktop.

## It's not working, what can I do?
You can ask me to take a look or raise a GitHub issue, but this is just a script developed for research purposes and nothing more, so no promises.

## Isn't scraping data from Facebook not allowed under the Terms?
Probably! I take no responsibility for any breach of Facebook's Terms if you use this script.


# LICENSE
MIT License

Copyright (c) 2023 Aaron McDonald

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.