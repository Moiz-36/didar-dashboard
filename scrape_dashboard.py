import time
import json
import os
from playwright.sync_api import sync_playwright

def scrape_dashboard():
    print("Launching browser script...")
    with sync_playwright() as p:
        # Launch browser headlessly
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Exact target URL requested
        url = "https://the.ismaili/programmes/pages-to-didar"
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait 5 seconds to ensure animations finish and calculations load completely
        print("Waiting for data layers to load...")
        page.wait_for_timeout(5000) 
        
        # Extract main text header blocks using specific structural indices
        print("Extracting main total metrics...")
        pages_read = page.locator(".rd-stat:nth-child(1) .rd-stat__num").text_content().strip()
        participants = page.locator(".rd-stat:nth-child(2) .rd-stat__num").text_content().strip()
        screen_free = page.locator(".rd-stat:nth-child(3) .rd-stat__num").text_content().strip()
        
        # Build core data dictionary
        data = {
            "pages_read": pages_read,
            "participants": participants,
            "screen_free_time": screen_free,
            "leaderboard": []
        }
        
        # Extract individual rows for the dynamic bar chart layout
        print("Extracting leaderboards/center participation details...")
        rows = page.locator(".rd-board__row").all()
        
        for row in rows:
            city_name = row.locator(".rd-board__label").text_content().strip()
            value_raw = row.locator(".rd-board__value").text_content().strip()
            
            # Sanitize numeric types safely (e.g., convert "47h" -> 47)
            clean_value = int(value_raw.replace('h', '').replace(',', '').strip())
            
            data["leaderboard"].append({
                "city": city_name.upper(),  # Forces clean uppercase layout
                "value": clean_value
            })
            
        # Target path output settings
        # Change this string path if you want to output to a specific desktop folder
        output_file = "data.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Web scraper pipeline finished cleanly. Data saved to '{output_file}'")
        browser.close()

if __name__ == "__main__":
    scrape_dashboard()
