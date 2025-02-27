from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import sys

def main():
    # Read input from Apify
    print("Reading input...")
    input_data = json.load(sys.stdin)
    
    # Setup Chrome
    print("Setting up Chrome...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login to Facebook
        print("Logging into Facebook...")
        driver.get('https://www.facebook.com')
        
        email_element = driver.find_element(By.ID, "email")
        email_element.send_keys(input_data['facebookEmail'])
        
        pass_element = driver.find_element(By.ID, "pass")
        pass_element.send_keys(input_data['facebookPassword'])
        
        login_element = driver.find_element(By.NAME, "login")
        login_element.click()
        time.sleep(3)
        
        # Post to each group
        results = []
        for group_url in input_data['groups']:
            try:
                print(f"Posting to group: {group_url}")
                driver.get(group_url)
                time.sleep(3)
                
                # Click post box
                post_box = driver.find_element(By.CSS_SELECTOR, "[role='textbox']")
                post_box.click()
                time.sleep(1)
                
                # Enter message
                post_box.send_keys(input_data['message'])
                time.sleep(1)
                
                # Click post button
                post_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Post']")
                post_button.click()
                time.sleep(3)
                
                results.append({
                    "group": group_url,
                    "status": "success"
                })
                
            except Exception as e:
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
