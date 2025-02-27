from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import sys
import pickle
import os

def save_cookies(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)
    print("Cookies saved successfully")

def load_cookies(driver, path):
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    print("Cookies loaded successfully")

def login_with_cookies(driver, input_data):
    cookies_path = 'facebook_cookies.pkl'
    
    # First try to load existing cookies
    if os.path.exists(cookies_path):
        print("Found existing cookies, attempting to use them...")
        driver.get('https://www.facebook.com')
        load_cookies(driver, cookies_path)
        driver.refresh()
        time.sleep(3)
        
        # Check if we're still logged in
        if "login" not in driver.current_url:
            print("Successfully logged in with cookies")
            return True
    
    # If cookies don't exist or didn't work, do manual login
    print("Performing manual login...")
    driver.get('https://www.facebook.com')
    
    # Clear any existing cookies
    driver.delete_all_cookies()
    
    email_element = driver.find_element(By.ID, "email")
    email_element.send_keys(input_data['facebookEmail'])
    
    pass_element = driver.find_element(By.ID, "pass")
    pass_element.send_keys(input_data['facebookPassword'])
    
    login_element = driver.find_element(By.NAME, "login")
    login_element.click()
    
    print("Waiting for manual 2FA verification...")
    # Wait for user to complete 2FA and reach main feed
    wait = WebDriverWait(driver, 300)  # 5 minutes timeout
    wait.until(EC.url_contains('facebook.com/home.php'))
    
    print("Login successful, saving cookies...")
    save_cookies(driver, cookies_path)
    return True

def post_to_group(driver, group_url, message):
    print(f"Posting to group: {group_url}")
    driver.get(group_url)
    time.sleep(5)  # Wait for group page to load
    
    # Wait for post box and click it
    wait = WebDriverWait(driver, 10)
    post_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[role='textbox']")))
    post_box.click()
    time.sleep(2)
    
    # Enter message
    post_box.send_keys(message)
    time.sleep(2)
    
    # Find and click post button
    post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Post']")))
    post_button.click()
    time.sleep(5)  # Wait for post to complete

def main():
    print("Starting Facebook Group Poster...")
    
    # Read input
    input_data = json.load(sys.stdin)
    
    # Setup Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    # Remove headless mode to allow manual 2FA
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login handling
        if not login_with_cookies(driver, input_data):
            raise Exception("Login failed")
        
        # Post to each group
        results = []
        for group_url in input_data['groups']:
            try:
                post_to_group(driver, group_url, input_data['message'])
                results.append({
                    "group": group_url,
                    "status": "success"
                })
            except Exception as e:
                print(f"Error posting to {group_url}: {str(e)}")
                results.append({
                    "group": group_url,
                    "status": "failed",
                    "error": str(e)
                })
        
        print(json.dumps({"success": True, "results": results}))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
