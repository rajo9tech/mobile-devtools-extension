import asyncio
import random
import time
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from fake_useragent import UserAgent

class AjioPlaywrightScraper:
    def __init__(self):
        # Configuration
        self.OUTPUT_DIR = "output"
        self.OUTPUT_FILE_CSV = "ajio_men_grooming_products.csv"
        self.OUTPUT_FILE_JSON = "ajio_products.json"
        self.SCROLL_PAUSE_TIME = random.uniform(2, 4)
        self.AJIO_URL = "https://www.ajio.com/s/min-50-percent-off-3348-44441?srsltid=AfmBOoq7Me3ahSZUkzd8rTyKjMw0u5YRCAmQARiSPyJ8mYK0yIvQxijY"

        # Oxylabs Proxy Configuration
        self.PROXY_CREDENTIALS = {
            "USERNAME": "Techy_46p30",
            "PASSWORD": "Techy_20+80=100",
            "PROXY_HOST": "pr.oxylabs.io",
            "PROXY_PORT": "7777"
        }

        # Proxy pool for rotation
        self.PROXY_POOL = [
            {
                "server": f"http://{self.PROXY_CREDENTIALS['PROXY_HOST']}:{self.PROXY_CREDENTIALS['PROXY_PORT']}",
                "username": self.PROXY_CREDENTIALS['USERNAME'],
                "password": self.PROXY_CREDENTIALS['PASSWORD']
            },
            {
                "server": f"http://us-{self.PROXY_CREDENTIALS['PROXY_HOST'].replace('pr.', 'pr.')}:10000",
                "username": self.PROXY_CREDENTIALS['USERNAME'],
                "password": self.PROXY_CREDENTIALS['PASSWORD']
            },
            {
                "server": f"http://gb-{self.PROXY_CREDENTIALS['PROXY_HOST'].replace('pr.', 'pr.')}:20000",
                "username": self.PROXY_CREDENTIALS['USERNAME'],
                "password": self.PROXY_CREDENTIALS['PASSWORD']
            }
        ]

        # User agents pool
        self.ua = UserAgent()

        # Headers pool for rotation
        self.HEADERS_POOL = [
            {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            },
            {
                'Accept-Language': 'en-GB,en;q=0.8,es;q=0.6',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'DNT': '0',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin'
            }
        ]

    def get_random_proxy(self):
        """Get a random proxy from the pool for IP rotation."""
        return random.choice(self.PROXY_POOL)

    def get_random_headers(self):
        """Get random headers for each request."""
        return random.choice(self.HEADERS_POOL)

    def get_random_viewport(self):
        """Generate random viewport size to mimic different devices."""
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864},
            {'width': 1280, 'height': 720}
        ]
        return random.choice(viewports)

    async def random_delay(self, min_sec=1, max_sec=3):
        """Random delay to mimic human behavior."""
        delay = random.uniform(min_sec, max_sec)
        print(f"⏳ Random delay: {delay:.2f} seconds")
        await asyncio.sleep(delay)

    async def simulate_human_mouse_movement(self, page):
        """Simulate realistic mouse movements."""
        try:
            # Get viewport size
            viewport = await page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")

            # Generate random mouse movements
            for _ in range(random.randint(3, 7)):
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)

                # Move mouse with some randomness
                await page.mouse.move(x, y)
                await self.random_delay(0.1, 0.3)

                # Occasionally add a click
                if random.random() < 0.3:
                    await page.mouse.click(x, y)
                    await self.random_delay(0.2, 0.5)

        except Exception as e:
            print(f"⚠️ Mouse simulation error: {e}")

    async def init_browser(self):
        """Initialize browser with stealth mode, proxy, and realistic settings."""
        playwright = await async_playwright().start()

        # Get random proxy for this session
        proxy = self.get_random_proxy()
        print(f"🌍 Using proxy: {proxy['server']}")

        # Launch browser with proxy
        browser = await playwright.chromium.launch(
            headless=True,
            proxy=proxy,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ]
        )

        # Create context with random viewport and headers
        viewport = self.get_random_viewport()
        headers = self.get_random_headers()

        context = await browser.new_context(
            user_agent=self.ua.random,
            viewport=viewport,
            extra_http_headers=headers,
            java_script_enabled=True,
            accept_downloads=False,
            ignore_https_errors=True
        )

        # Create page
        page = await context.new_page()

        # Apply stealth mode
        await stealth_async(page)

        return playwright, browser, context, page

    async def wait_for_page_load(self, page):
        """Wait for page to fully load with multiple strategies."""
        try:
            print("📄 Waiting for page to load...")

            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=30000)

            # Wait for specific content
            await page.wait_for_selector('body', timeout=15000)

            # Additional wait for dynamic content
            await self.random_delay(2, 4)

            print("✅ Page loaded successfully")

        except Exception as e:
            print(f"⚠️ Page load timeout, continuing anyway: {e}")

    async def scroll_to_load_all(self, page):
        """Scroll page gradually to load all products with human-like behavior."""
        print("🔄 Starting scroll to load all products...")

        try:
            # Get initial page height
            last_height = await page.evaluate("document.body.scrollHeight")

            scroll_count = 0
            max_scrolls = 50  # Prevent infinite scrolling

            while scroll_count < max_scrolls:
                print(f"📏 Scroll #{scroll_count + 1} - Page height: {last_height}")

                # Simulate human scrolling behavior
                scroll_distance = random.randint(300, 800)

                # Smooth scroll
                await page.evaluate(f"""
                    window.scrollBy({{
                        top: {scroll_distance},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)

                # Random pause between scrolls
                await self.random_delay(self.SCROLL_PAUSE_TIME, self.SCROLL_PAUSE_TIME + 2)

                # Simulate mouse movement during scroll
                await self.simulate_human_mouse_movement(page)

                # Check if new content loaded
                new_height = await page.evaluate("document.body.scrollHeight")

                if new_height == last_height:
                    print("📏 No new content loaded, checking again...")
                    # Try scrolling a bit more and wait
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    await self.random_delay(3, 5)

                    final_height = await page.evaluate("document.body.scrollHeight")
                    if final_height == new_height:
                        print("✅ Scrolling completed - no more content to load")
                        break

                last_height = new_height
                scroll_count += 1

        except Exception as e:
            print(f"⚠️ Error during scrolling: {e}")

    async def extract_products(self, page):
        """Extract all product information from the page."""
        print("📊 Extracting product information...")

        try:
            # Wait for products to be present
            await page.wait_for_selector(".item.rilrtl-products-list__item", timeout=15000)

            # Get all product containers
            product_containers = await page.query_selector_all(".item.rilrtl-products-list__item")
            print(f"🎯 Found {len(product_containers)} product containers")

            data = []
            missed = 0

            for i, container in enumerate(product_containers):
                try:
                    # Extract brand
                    brand_element = await container.query_selector("div[class*='brand']")
                    brand = await brand_element.text_content() if brand_element else "N/A"
                    brand = brand.strip()

                    # Extract name
                    name_element = await container.query_selector("div[class*='name false'], div[class*='name']")
                    name = await name_element.text_content() if name_element else "N/A"
                    name = name.strip()

                    # Extract rating
                    rating_element = await container.query_selector("p[class*='_3I65V'], div[class*='rating']")
                    rating = await rating_element.text_content() if rating_element else None
                    if rating:
                        rating = rating.strip()

                    # Extract original price
                    original_price_element = await container.query_selector("span[class*='original-price']")
                    original_price = await original_price_element.text_content() if original_price_element else "N/A"
                    original_price = original_price.strip().replace(",", "").replace("₹", "")

                    # Extract discount price
                    discount_price_element = await container.query_selector("span[id*='price-value'], span[class*='price-value']")
                    discount_price = await discount_price_element.text_content() if discount_price_element else "N/A"
                    discount_price = discount_price.strip()

                    # Extract discount percentage
                    discount_element = await container.query_selector("span[class*='discount']")
                    discount = await discount_element.text_content() if discount_element else "N/A"
                    discount = discount.strip()

                    # Extract product link
                    link_element = await container.query_selector("a[class*='rilrtl-products-list__link'], a")
                    product_link = await link_element.get_attribute("href") if link_element else "N/A"
                    if product_link and not product_link.startswith("http"):
                        product_link = "https://www.ajio.com" + product_link

                    # Extract image URL
                    img_element = await container.query_selector("img")
                    img_url = await img_element.get_attribute("src") if img_element else "N/A"
                    if not img_url:
                        img_url = await img_element.get_attribute("data-src") if img_element else "N/A"

                    product_data = {
                        "Product Name": name,
                        "Brand": brand,
                        "Original Price": original_price,
                        "Discount Price": discount_price,
                        "Discount%": discount,
                        "Rating": rating,
                        "Product Link": product_link,
                        "Image URL": img_url,
                        "Scraped At": datetime.now().isoformat()
                    }

                    data.append(product_data)

                    if (i + 1) % 10 == 0:
                        print(f"✅ Processed {i + 1} products...")

                except Exception as e:
                    print(f"⚠️ Error extracting product {i + 1}: {e}")
                    missed += 1
                    continue

            print(f"✅ Products extracted: {len(data)}")
            print(f"⚠️ Products missed: {missed}")
            return data

        except Exception as e:
            print(f"❌ Critical error during extraction: {e}")
            return []

    async def save_data(self, data):
        """Save extracted data to CSV and JSON files."""
        if not data:
            print("❌ No data to save")
            return

        # Create output directory
        Path(self.OUTPUT_DIR).mkdir(exist_ok=True)

        # Save to CSV
        csv_path = Path(self.OUTPUT_DIR) / self.OUTPUT_FILE_CSV
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"📁 Data saved to CSV: {csv_path}")

        # Save to JSON
        json_path = Path(self.OUTPUT_DIR) / self.OUTPUT_FILE_JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"📁 Data saved to JSON: {json_path}")

        print(f"📊 Total products saved: {len(data)}")

    async def run(self):
        """Main execution method."""
        playwright = None
        browser = None

        try:
            print("🚀 Starting AJIO Playwright Scraper...")
            print("🔧 Initializing browser with stealth mode and proxy...")

            # Initialize browser
            playwright, browser, context, page = await self.init_browser()

            # Navigate to AJIO
            print(f"🌐 Navigating to: {self.AJIO_URL}")
            await page.goto(self.AJIO_URL, timeout=60000)

            # Wait for page to load
            await self.wait_for_page_load(page)

            # Simulate human behavior before starting
            await self.simulate_human_mouse_movement(page)
            await self.random_delay(2, 4)

            # Scroll to load all products
            await self.scroll_to_load_all(page)

            # Extract products
            products = await self.extract_products(page)

            # Save data
            await self.save_data(products)

            print("🎉 Scraping completed successfully!")

        except Exception as e:
            print(f"❌ Critical error: {e}")
            raise

        finally:
            # Cleanup
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

async def main():
    """Entry point for the scraper."""
    scraper = AjioPlaywrightScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
