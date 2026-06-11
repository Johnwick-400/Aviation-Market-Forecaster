import asyncio
import os
import glob
import shutil
from playwright.async_api import async_playwright

async def main():
    print("Launching standard Playwright to extract BTS T-100 Domestic Data...")
    downloads_dir = os.path.expanduser("~/Downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Configure download path
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        print("Navigating to BTS Form 41 page...")
        await page.goto("https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FMF", timeout=60000)
        
        # Wait for the table to load
        await page.wait_for_selector("table", timeout=15000)
        
        # The fields requested: ORIGIN, DEST, YEAR, MONTH, PASSENGERS
        # Uncheck all first or just check the specific ones?
        # Usually PASSENGERS is checked by default. Let's explicitly check them.
        
        fields = ["PASSENGERS", "ORIGIN", "DEST", "YEAR", "MONTH"]
        for field in fields:
            print(f"Checking {field}...")
            # BTS fields usually have labels or input values matching the field names
            # We can find the input checkbox by its corresponding label or value
            try:
                # The exact HTML structure of BTS might vary, but they generally use input values matching the column names
                checkbox = page.locator(f"input[type='checkbox'][value='{field}']")
                if await checkbox.count() > 0:
                    if not await checkbox.is_checked():
                        await checkbox.check()
                else:
                    print(f"Could not find exact value for {field}, trying by text...")
            except Exception as e:
                print(f"Error checking {field}: {e}")
        
        print("Clicking Download...")
        # Start waiting for the download
        async with page.expect_download(timeout=60000) as download_info:
            # Click the Download button (Usually an input or button with value/text 'Download')
            await page.locator("input[value='Download'], button:has-text('Download')").first.click()
            
        download = await download_info.value
        file_path = os.path.join(downloads_dir, download.suggested_filename)
        print(f"Downloading to {file_path}...")
        await download.save_as(file_path)
        
        print(f"✅ Saved to {file_path}")
        await browser.close()
        
        # Move to destination
        dest = "/home/pavan_veesam/poc-main/market-forecaster/data/raw/bts_t100.csv"
        shutil.move(file_path, dest)
        print(f"✅ Successfully moved to {dest}")

if __name__ == "__main__":
    asyncio.run(main())