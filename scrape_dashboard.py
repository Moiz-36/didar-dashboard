import time
import json
import os
from playwright.sync_api import sync_playwright

def scrape_dashboard():
    print("Launching browser script...")
    with sync_playwright() as p:
        # Prevent automated browser detection blocks on cloud servers
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        # Emulate a standard desktop user profile
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://the.ismaili/programmes/pages-to-didar"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="load")
        
        print("Waiting for dashboard visual components to render...")
        page.wait_for_timeout(7000) 
        
        # FIXED: Corrected indentation for the data dictionary block
        print("Extracting main total metrics...")
        data = {
            "pages_read": page.locator(".rd-stat:nth-child(1) .rd-stat__num").text_content().strip(),
            "participants": page.locator(".rd-stat:nth-child(2) .rd-stat__num").text_content().strip(),
            "screen_free_time": page.locator(".rd-stat:nth-child(3) .rd-stat__num").text_content().strip(),
            "leaderboard": [],
            "age_groups": []  
        }
        
        # 1. Gather Center Participation Data rows
        print("Scraping leaderboard rankings...")
        rows = page.locator(".rd-board__row").all()
        for row in rows:
            city_name = row.locator(".rd-board__label").text_content().strip()
            value_raw = row.locator(".rd-board__value").text_content().strip()
            clean_value = int(value_raw.replace('h', '').replace(',', '').strip())
            data["leaderboard"].append({"city": city_name.upper(), "value": clean_value})

        # 2. Gather Readers By Age Data rows
        print("Scraping age bracket breakdowns...")
        try:
            age_rows = page.locator(".rd-age__row").all()
            for a_row in age_rows:
                band = a_row.locator(".rd-age__band").text_content().strip()
                count_raw = a_row.locator(".rd-age__count").text_content().strip()
                data["age_groups"].append({
                    "band": band,
                    "count": int(count_raw.replace(',', '').strip())
                })
            print(f"Successfully found {len(data['age_groups'])} age brackets.")
        except Exception as age_err:
            print(f"Warning: Could not parse age brackets: {age_err}")

        # Save output inside workspace folder
        output_file = "data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Scrape execution complete! Local file update written to '{output_file}'")
        browser.close()

if __name__ == "__main__":
    scrape_dashboard()
