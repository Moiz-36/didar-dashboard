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
        
        # Build core data dictionary with correct Python indentation
        print("Extracting main total metrics...")
        data = {
            "pages_read": page.locator(".rd-stat:nth-child(1) .rd-stat__num").text_content().strip(),
            "participants": page.locator(".rd-stat:nth-child(2) .rd-stat__num").text_content().strip(),
            "screen_free_time": page.locator(".rd-stat:nth-child(3) .rd-stat__num").text_content().strip(),
            "leaderboard": [],
            "age_groups": [] 
        }
        
        # 1. Extract individual rows for Center Participation
        print("Extracting leaderboard/center participation details...")
        rows = page.locator(".rd-board__row").all()
        for row in rows:
            city_name = row.locator(".rd-board__label").text_content().strip()
            value_raw = row.locator(".rd-board__value").text_content().strip()
            clean_value = int(value_raw.replace('h', '').replace(',', '').strip())
            data["leaderboard"].append({"city": city_name.upper(), "value": clean_value})

        # 2. Extract rows for Readers by Age Automatically
        print("Extracting age distribution categories...")
        age_rows = page.locator(".rd-age__row").all()
        for a_row in age_rows:
            band = a_row.locator(".rd-age__band").text_content().strip()
            count_raw = a_row.locator(".rd-age__count").text_content().strip()
            data["age_groups"].append({
                "band": band,
                "count": int(count_raw.replace(',', '').strip())
            })
            
        # Target path output settings
        output_file = "data.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Web scraper pipeline finished cleanly. Data saved to '{output_file}'")
        browser.close()

if __name__ == "__main__":
    # If running locally on your PC 24/7, this loop keeps it running every 5 minutes.
    # If running on GitHub Actions via the scrape.yml timer, you can leave this loop in,
    # or let GitHub handle the scheduling on its own cloud servers!
    while True:
        try:
            scrape_dashboard()
        except Exception as e:
            print(f"Error encountered during scrape: {e}")
            
        print("Sleeping for 5 minutes before next live update...")
        time.sleep(300) # 300 seconds = 5 minutes
