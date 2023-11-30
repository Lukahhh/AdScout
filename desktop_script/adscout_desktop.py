from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import traceback
import csv

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
csv_file_path = 'csv/scraped_data.csv'

# Configure the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Update if your path is different

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

# Set the window size to a standard desktop size
driver.set_window_size(1920, 1080)

# Navigate to Facebook
driver.get('https://www.facebook.com')


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
        time.sleep(1)  # Short sleep to allow for loading

    # Scroll back to the top of the page
    driver.execute_script("window.scrollTo(0, 0);")

    # Set to track the index of the last post processed in the last scroll
    last_processed_index = -1

    # Adjust the range for your needs
    for _ in range(100):
        try:
            posts = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='x1lliihq']")))
            print(f"Found {len(posts)} posts in the current view.")

            for index, post in enumerate(posts):
                if index <= last_processed_index:
                    continue  # Skip posts that were processed in the last scroll

                # Scroll the post to the top of the page
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                # Additional scroll up to adjust for fixed headers, etc.
                driver.execute_script("window.scrollBy(0, -100);")

                # Dynamic wait after scrolling
                time.sleep(1)

                # Take a screenshot of the post
                screenshot_name = f'post_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                driver.save_screenshot(screenshot_name)

                # Open the image and enhance it
                image = Image.open(screenshot_name)
                image = ImageEnhance.Contrast(image).enhance(2)  # Increase contrast
                image = ImageEnhance.Sharpness(image).enhance(2)  # Increase sharpness

                # Optional: Resize the image to double the size
                image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)

                # Use pytesseract to do OCR on the image with custom configurations
                custom_oem_psm_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_oem_psm_config)

                # Use pytesseract to do OCR on the image and get bounding box information for text
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

                # Initialize a flag to determine if a sponsored post is found near the top
                sponsored_post_near_top = False

                # Define the maximum y-coordinate (distance from the top) for a 'Sponsored' label to be considered near the top of the image
                max_y_threshold = image.height * 0.25  # You can adjust this threshold as needed

                # Iterate through the detected text items
                for i, word in enumerate(ocr_data['text']):
                    if 'Sponsored' in word:
                        x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
                        
                        # Check if the 'Sponsored' text's y-coordinate is within the threshold from the top
                        if y < max_y_threshold:
                            sponsored_post_near_top = True
                            break

                # Take actions based on whether a sponsored post is near the top
                if sponsored_post_near_top:
                    # Save the screenshot and/or perform other actions
                    print(f"Sponsored ad found near the top in {screenshot_name}")
                    # Rename the screenshot for sponsored posts
                    os.rename(screenshot_name, f'sponsored_ad_{screenshot_name}')
                    # Assuming 'post' is the current sponsored post WebElement
                    # Initialize default values
                    profile_url = "Not Available"
                    profile_title = "Not Available"
                    visible_url = "Not Available"
                    ad_destination_url = "Not Available"
                    call_to_action = "Not Available"

                    try:
                        # Extract profile URL and title
                        h4_element = post.find_element(By.TAG_NAME, "h4")
                        a_element = h4_element.find_element(By.TAG_NAME, "a")
                        profile_url = a_element.get_attribute('href')
                        profile_title = a_element.text

                        # Inside your loop, after extracting the profile title
                        status = "Uncategorized"  # Default status
                        if profile_title in whitelist:
                            status = "Whitelisted"
                        elif profile_title in blacklist:
                            status = "Blacklisted"

                    except Exception as e:
                        print(f"Profile URL/Title not found: {e}")

                    try:
                        # Extract visible URL
                        visible_url_element = post.find_element(By.CSS_SELECTOR, "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft")
                        visible_url = visible_url_element.text
                    except Exception as e:
                        print(f"Visible URL not found: {e}")

                    try:
                        # Extract ad destination URL
                        ad_link_element = post.find_element(By.CSS_SELECTOR, "a.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x87ps6o.x1lku1pv.x1a2a7pz.x9f619.x3nfvp2.xdt5ytf.xl56j7k.x1n2onr6.xh8yej3")
                        ad_destination_url = ad_link_element.get_attribute('href')
                    except Exception as e:
                        print(f"Ad destination URL not found: {e}")

                    try:
                        # Extract call to action text
                        call_to_action_element = post.find_element(By.CSS_SELECTOR, "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6")
                        call_to_action = call_to_action_element.text
                    except Exception as e:
                        print(f"Call to action not found: {e}")

                    # Append the data to CSV or perform other actions
                    data_row = [screenshot_name, profile_title, status, profile_url, visible_url, ad_destination_url, call_to_action,user_agent]
                    append_to_csv(csv_file_path, data_row)
                    
                else:
                    # If no sponsored post is near the top, delete the screenshot
                    print(f"No 'Sponsored' ad found near the top - deleting screenshot")
                    os.remove(screenshot_name)

                # Update the last processed index
                last_processed_index = index

        except Exception as e:
            print("Error during processing posts: ", str(e))
            traceback.print_exc()

        # Scroll down to load new posts
        try:
            print(f"Scrolling to load more posts after processing {last_processed_index + 1} posts")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new posts to load
        except Exception as e:
            print("Error during scrolling: ", str(e))
            traceback.print_exc()

    # Close the driver
    driver.quit()

except Exception as e:
    print("An error occurred in the script: ", str(e))
    traceback.print_exc()
