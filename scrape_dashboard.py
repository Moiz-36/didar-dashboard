import time
import json
import os
from playwright.sync_api import sync_playwright

def scrape_dashboard():
    print("Launching browser script inside GitHub cloud container...")
    with sync_playwright() as p:
        # Launch headless browser with anti-detection flags
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        # Emulate a premium high-resolution desktop machine context
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 3840, "height": 2160} # Force a 4K viewport so all side components render
        )
        page = context.new_page()
        
        url = "https://the.ismaili/programmes/pages-to-didar"
        print(f"Navigating to web target link: {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        print("Waiting for page animations and data layouts to settle...")
        page.wait_for_timeout(10000) # Give it a full 10 seconds to fetch data layers
        
        # Explicitly verify key elements exist before pulling text fields
        print("Locating master metric layers...")
        try:
            page.wait_for_selector(".rd-stat__num", timeout=15000)
        except Exception as e:
            print(f"CRITICAL ERROR: Page elements failed to render in time: {e}")
            browser.close()
            return

        # Core target dictionary mapping structure
        data = {
            "pages_read": page.locator(".rd-stat:nth-child(1) .rd-stat__num").text_content().strip(),
            "participants": page.locator(".rd-stat:nth-child(2) .rd-stat__num").text_content().strip(),
            "screen_free_time": page.locator(".rd-stat:nth-child(3) .rd-stat__num").text_content().strip(),
            "leaderboard": [],
            "age_groups": []  
        }
        
        # 1. Parse Center Participation Array
        print("Scraping center participation leaderboard rows...")
        rows = page.locator(".rd-board__row").all()
        for row in rows:
            city_name = row.locator(".rd-board__label").text_content().strip()
            value_raw = row.locator(".rd-board__value").text_content().strip()
            clean_value = int(value_raw.replace('h', '').replace(',', '').strip())
            data["leaderboard"].append({"city": city_name.upper(), "value": clean_value})
        print(f"Successfully processed {len(data['leaderboard'])} city records.")

        # 2. Parse Readers by Age Array with enhanced cloud selectors
        print("Scraping age segment categories...")
        try:
            # Force the cloud scripter to wait until the age section is fully visible
            page.wait_for_selector(".rd-age__row", timeout=10000)
            
            # Target the rows explicitly inside the age panel block container
            age_rows = page.locator(".rd-age .rd-age__row").all()
            for a_row in age_rows:
                band = a_row.locator(".rd-age__band").text_content().strip()
                count_raw = a_row.locator(".rd-age__count").text_content().strip()
                data["age_groups"].append({
                    "band": band,
                    "count": int(count_raw.replace(',', '').strip())
                })
            print(f"Successfully processed {len(data['age_groups'])} age categories.")
        except Exception as age_err:
            print(f"Warning/Error: Age categories could not be completely parsed: {age_err}")

        # Save finalized file payload inside workspace root
        output_file = "data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Pipeline executed successfully. Fresh entries saved directly to '{output_file}'")
        browser.close()

if __name__ == "__main__":
    scrape_dashboard()
