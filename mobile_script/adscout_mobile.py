from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
# import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import traceback
import csv
# from selenium.webdriver.common.keys import Keys



# Define whitelist and blacklist
whitelist = set([
    "HubSpot",
    "JADED MAN",
    "Trans.au",
    "The Timesheet Man",
    ])
blacklist = set([
    "Untrusted Service 1", 
    "Untrusted Service 2"
    ])

def append_to_csv(file_path, data):
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# CSV File
csv_file_path = 'csv/scraped_mobile_data.csv'
status=""
ad_type=""
notes=""

# Configure the path to the tesseract executable
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Update if your path is different

# Set Chrome options for remote debugging
chrome_options = Options()
#desktop
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
#mobile
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")


# Path to ChromeDriver
chrome_driver_path = '/Users/aaronmcdonald/chromedriver-mac-x64/chromedriver'
service = Service(chrome_driver_path)

# Connect to the already-opened Chrome session
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the Facebook webpage
    driver.get('https://www.facebook.com')
    wait = WebDriverWait(driver, 10)

    # Wait for initial page load
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//body')))
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.quit()
        exit()

    # Initial scrolling phase to load and cache posts
    end_time = time.time() + 5  # Scroll for 60 seconds
    while time.time() < end_time:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Short sleep to allow for loading

    # Scroll back to the top of the page
    driver.execute_script("window.scrollTo(0, 0);")

    # Set to track the index of the last post processed in the last scroll

    last_processed_index = -1
    for _ in range (35):
        try:
            # Fetch all potential posts with specific attributes
            potential_posts = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-tracking-duration-id and @data-actual-height>100]")))
            print(f"Found {len(potential_posts)} posts in the news feed.")

            # Filter to keep only posts that contain the word "Sponsored"
            # posts = [post for post in potential_posts if "Sponsored" in post.text]

            # Filter to keep only posts that contain the word "Sponsored"
            posts = []
            for post in potential_posts:
                try:
                    # Search for an element within the post that contains the text "Sponsored"
                    if post.find_element(By.XPATH, ".//*[contains(text(), 'Sponsored')]"):
                        posts.append(post)
                        
                except Exception:
                    # This exception will occur if the "Sponsored" text is not found, meaning it's not an ad post
                    pass

            print(f"Found {len(posts)} SPONSORED posts in the news feed.")

            # Check if there are new posts to process
            if not posts:
                break

            for index, post in enumerate(posts):
                if index <= last_processed_index:
                    continue  # Skip posts that were processed in the last scroll

                # Scroll the post to the top of the page
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                # Additional scroll up to adjust for fixed headers, etc.
                driver.execute_script("window.scrollBy(0, -100);")

                # Dynamic wait after scrolling
                time.sleep(3)

                # Take a screenshot of the post
                screenshot_name = f'post_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                driver.save_screenshot(screenshot_name)

                # Rename the screenshot for sponsored posts
                os.rename(screenshot_name, f'sponsored_ad_{screenshot_name}')
                # Assuming 'post' is the current sponsored post WebElement
                # Initialize default values
                profile_url = "Not Available"
                profile_title = "Not Available"
                visible_url = "Not Available"
                ad_destination_url = "Not Available"
                call_to_action = "Not Available"

                # Attempt to extract profile title
            
                try:
                    # Assuming 'post' is a WebElement representing the current sponsored post
                    visible_url_element = post.find_element(By.XPATH, ".//div[contains(@class, 'native-text') and contains(@style, 'color:#65676b')]/span[contains(@class, 'f5')]")
                    visible_url = visible_url_element.text
                except NoSuchElementException:
                    visible_url = "Not Available"


                try:
                    profile_title = ""
                    profile_url = ""
                    profile_title_element = post.find_element(By.XPATH, ".//span[contains(@class, 'rtl-ignore f2 a')]")
                    profile_title = profile_title_element.text
                    # print(profile_title)
                
                except NoSuchElementException:
                    print("Element not found")

                try:
                    # Use JavaScript to perform the click
                    driver.execute_script("arguments[0].click();", profile_title_element)
                    time.sleep(3)

                    profile_url = driver.current_url

                    driver.execute_script("window.history.go(-1)")

                except NoSuchElementException:
                    print("Element not found")
                except TimeoutException:
                    print("Timed out waiting for element to appear")
                except Exception as e:
                    print(f"An error occurred: {e}")

                except NoSuchElementException:
                    profile_title = "Not Available"
                    profile_url = "Not Available"


                # Append the data to CSV or perform other actions
                data_row = [screenshot_name, profile_title, ad_type, status, profile_url, visible_url,notes]
                append_to_csv(csv_file_path, data_row)
                # print(profile_title + " – " + visible_url + " - " + profile_url)
                # os.remove(screenshot_name)
                # Update the last processed index
                last_processed_index = index

        except Exception as e:
            print("Error during processing posts: ", str(e))
            traceback.print_exc()

        try:
            print(f"Scrolling to load more posts after processing {last_processed_index + 1} posts")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)  # Wait for new posts to load
        except Exception as e:
            print("Error during scrolling: ", str(e))
            traceback.print_exc()


except Exception as e:
    print("An error occurred in the script: ", str(e))
    traceback.print_exc()
