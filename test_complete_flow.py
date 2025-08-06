#!/usr/bin/env python3
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_backend_api():
    """Test the backend API directly"""
    print("=== Testing Backend API ===")
    
    # Create a test file
    with open('test.raw', 'w') as f:
        f.write('test raw file content')
    
    # Upload file to Flask app
    url = 'http://localhost:9847/upload'
    files = {'file': ('test.raw', open('test.raw', 'rb'), 'application/octet-stream')}
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'summary' in data:
                summary = data['summary']
                print(f"Summary keys: {list(summary.keys())}")
                print(f"Summary data: {summary}")
                
                # Check pressure units
                if 'min_pressure' in summary:
                    print(f"Min pressure: {summary['min_pressure']} (should be in bar)")
                    print(f"Max pressure: {summary['max_pressure']} (should be in bar)")
                    print(f"Mean pressure: {summary['mean_pressure']} (should be in bar)")
            else:
                print("No 'summary' key in response!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Backend test failed: {e}")
    finally:
        files['file'][1].close()

def test_frontend():
    """Test the frontend with Selenium"""
    print("\n=== Testing Frontend ===")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    
    try:
        # Initialize the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the app
        driver.get('http://localhost:9847')
        
        # Wait for page to load
        WebDriverWait(driver, 10).wait(
            EC.presence_of_element_located((By.ID, "fileInput"))
        )
        
        # Upload file
        file_input = driver.find_element(By.ID, "fileInput")
        file_input.send_keys('/Users/eddykapelczak/Documents/GitHub/labtracker-ios/test.raw')
        
        # Click upload button
        upload_btn = driver.find_element(By.ID, "uploadBtn")
        upload_btn.click()
        
        # Wait for results
        time.sleep(3)
        
        # Check console logs
        logs = driver.get_log('browser')
        print("Browser console logs:")
        for log in logs:
            print(f"  {log['level']}: {log['message']}")
        
        # Check if summary stats element exists and has content
        try:
            summary_stats = driver.find_element(By.ID, "summaryStats")
            print(f"Summary stats element found: {summary_stats is not None}")
            print(f"Summary stats innerHTML: {summary_stats.get_attribute('innerHTML')[:200]}...")
        except Exception as e:
            print(f"Summary stats element not found: {e}")
        
        # Check if results section is visible
        try:
            results = driver.find_element(By.ID, "results")
            print(f"Results section visible: {results.is_displayed()}")
        except Exception as e:
            print(f"Results section not found: {e}")
            
    except Exception as e:
        print(f"Frontend test failed: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_backend_api()
    test_frontend()