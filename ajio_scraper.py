#!/usr/bin/env python3
"""
AJIO Web Scraper - Main Module
Desktop-ready web scraper for AJIO products with proper file organization.
"""

import os
import re
import csv
import sys
import json
import time
import math
import random
import string
import asyncio
import argparse
import logging
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PWTimeout

from config import (
    USER_AGENTS, INDIA_GEO_HEADER, PROXY, POPUP_SELECTORS, POPUP_CLOSE_SELECTORS,
    SCROLL_MAX_PRODUCTS, SCROLL_MAX_MINUTES, SCROLL_HUMAN_STEP_MIN, SCROLL_HUMAN_STEP_MAX,
    SCROLL_WAIT_MIN_S, SCROLL_WAIT_MAX_S, SCROLL_IDLE_PINGS, SCROLL_UPWARDS_CHANCE,
    SCROLL_MOUSE_WIGGLE_CHANCE, DOM_GROWTH_STALL_REPEATS, DOM_GROWTH_AWAIT_S,
    FALLBACK_BOTTOM_SCROLL_ROUNDS, BOTTOM_STABLE_REPEATS, CARD_SELECTOR, LINK_SELECTOR,
    BRAND_SELECTORS, NAME_SELECTORS, PRICE_DISCOUNTED, PRICE_ORIGINAL, DISCOUNT_SELECTORS,
    IMG_HOLDER, DEFAULT_PREFIX, URL_DEFAULT
)
from utils import ts, log, randf, randbool, sanitize_price, uniq_name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ajio_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AjioScraper:
    """Main AJIO Scraper class with enhanced desktop compatibility"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    async def stealth_patch(self, page: Page) -> None:
        """Apply stealth patches to avoid detection"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'platform', { get: () => 'Linux armv8l' });
            Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

    async def close_popups(self, page: Page) -> None:
        """Close any popups that might appear"""
        try:
            for sel in POPUP_SELECTORS:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    log("⚠️ Popup detected")
                    # try obvious close targets inside popup
                    for close_sel in POPUP_CLOSE_SELECTORS:
                        btn = await el.query_selector(close_sel) or await page.query_selector(close_sel)
                        if btn and await btn.is_visible():
                            try:
                                await btn.click(timeout=1000)
                                log("✅ Popup closed")
                                await asyncio.sleep(randf(0.5, 1.5))
                                break
                            except Exception:
                                pass
        except Exception as e:
            log(f"❌ Popup handler error: {e}")

    async def wait_network_softidle(self, page: Page, timeout_ms: int = 4000) -> None:
        """Wait for network to be idle"""
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except PWTimeout:
            # Not critical; carry on
            pass

    async def count_cards(self, page: Page) -> int:
        """Count the number of product cards on page"""
        return await page.evaluate(f"document.querySelectorAll({json.dumps(CARD_SELECTOR)}).length")

    async def scroll_to_last_card(self, page: Page) -> None:
        """Scroll to the last product card"""
        js = f"""
        const cards = Array.from(document.querySelectorAll({json.dumps(CARD_SELECTOR)}));
        if (cards.length) {{
            cards[cards.length - 1].scrollIntoView({{behavior: 'instant', block: 'center'}});
        }}
        """
        await page.evaluate(js)

    async def human_mouse_wiggle(self, page: Page) -> None:
        """Simulate human-like mouse movement"""
        try:
            vp = page.viewport_size or {"width": 1280, "height": 800}
            w, h = vp["width"], vp["height"]
            x = random.randint(int(w*0.2), int(w*0.8))
            y = random.randint(int(h*0.2), int(h*0.8))
            await page.mouse.move(x, y, steps=random.randint(10, 24))
            # optional hover on random card
            if randbool(0.5):
                await page.hover(CARD_SELECTOR)
        except Exception:
            pass

    async def human_scroll_cycle(self, page: Page) -> None:
        """Perform human-like scrolling behavior"""
        # occasional short idle (simulates reading)
        if randbool(0.10):
            idle_s = random.randint(*SCROLL_IDLE_PINGS)
            log(f"🧍 Idling for {idle_s}s")
            await asyncio.sleep(idle_s)

        # upward nudge sometimes
        if randbool(SCROLL_UPWARDS_CHANCE):
            step = randf(0.15, 0.4)
            await page.evaluate(f"window.scrollBy(0, -window.innerHeight * {step});")
            await asyncio.sleep(randf(0.4, 0.9))

        # main downward step
        step = randf(SCROLL_HUMAN_STEP_MIN, SCROLL_HUMAN_STEP_MAX)
        await page.evaluate(f"window.scrollBy(0, window.innerHeight * {step});")
        await asyncio.sleep(randf(SCROLL_WAIT_MIN_S, SCROLL_WAIT_MAX_S))

        # occasional mouse wiggle
        if randbool(SCROLL_MOUSE_WIGGLE_CHANCE):
            await self.human_mouse_wiggle(page)

    async def await_dom_growth(self, page: Page, prev_count: int) -> int:
        """Wait a short time to see if new cards mount (lazy loading)."""
        window_s = randf(*DOM_GROWTH_AWAIT_S)
        await asyncio.sleep(window_s)
        return await self.count_cards(page)

    async def persistent_bottom_scroll(self, page: Page, target_max: int) -> None:
        """Fallback scrolling method - scroll to bottom persistently"""
        log("✨ Fallback: persistent scroll-to-bottom (until true end)")
        prev_count = await self.count_cards(page)
        stable = 0
        round_num = 0

        while True:
            round_num += 1
            await self.close_popups(page)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            log(f"⬇️ Bottom scroll (round {round_num})")

            await self.wait_network_softidle(page, timeout_ms=5000)
            await asyncio.sleep(randf(2.0, 4.5))

            new_count = await self.count_cards(page)
            log(f"📦 Products loaded: {new_count}")

            if new_count >= target_max:
                log("⚡ Reached target max products (safety cap). Stopping.")
                break

            if new_count == prev_count:
                stable_height = await page.evaluate("document.body.scrollHeight")
                await asyncio.sleep(randf(1.0, 2.0))
                stable_height2 = await page.evaluate("document.body.scrollHeight")
                if stable_height2 == stable_height:
                    stable += 1
                    log(f"⚠️ No growth & height stable ({stable}/{BOTTOM_STABLE_REPEATS})")
                    if stable >= BOTTOM_STABLE_REPEATS:
                        log("🛑 Detected end of product list — stopping scroll.")
                        break
                else:
                    stable = 0
            else:
                stable = 0

            prev_count = new_count

            if round_num >= FALLBACK_BOTTOM_SCROLL_ROUNDS:
                log("🛑 Reached maximum scroll rounds. Stopping.")
                break

    async def load_all_products(self, page: Page, max_products: int, max_minutes: float) -> None:
        """Load all products using progressive scrolling"""
        t0 = time.time()
        prev_count = 0
        flat = 0

        log("✨ Human-like progressive scrolling…")
        while True:
            await self.close_popups(page)
            await self.human_scroll_cycle(page)
            await self.wait_network_softidle(page, timeout_ms=3000)

            # nudge last card into center to trigger viewport-based loaders
            await self.scroll_to_last_card(page)

            # watch growth
            new_count = await self.await_dom_growth(page, prev_count)
            log(f"📦 Loaded {new_count} products so far…")

            if new_count >= max_products:
                log("⚡ Hit max_products limit for progressive scroll.")
                break

            if new_count == prev_count:
                flat += 1
                log(f"⚠️ DOM growth stalled ({flat}/{DOM_GROWTH_STALL_REPEATS})")
            else:
                flat = 0

            if flat >= DOM_GROWTH_STALL_REPEATS:
                log("✅ Progressive scroll stalled—switching to fallback.")
                break

            prev_count = new_count

            # time cap
            if (time.time() - t0) / 60.0 > max_minutes:
                log("🛑 Time cap reached for progressive scroll.")
                break

        # Fallback
        await self.persistent_bottom_scroll(page, max_products)

    async def extract_products(self, page: Page, base_url: str) -> List[Dict[str, Any]]:
        """Extract product data from the page"""
        log("🕵️ Extracting products (final short wait for lazy images)…")
        await asyncio.sleep(randf(2.0, 4.0))

        js = f"""
        (() => {{
            const items = [];
            const qs = (el, s) => el.querySelector(s);
            const qsa = (el, s) => Array.from(el.querySelectorAll(s));

            const CARD_SEL = {json.dumps(CARD_SELECTOR)};
            const LINK_SEL = {json.dumps(LINK_SELECTOR)};
            const BRAND_SEL = {json.dumps(BRAND_SELECTORS)};
            const NAME_SEL  = {json.dumps(NAME_SELECTORS)};
            const PRICE_D   = {json.dumps(PRICE_DISCOUNTED)};
            const PRICE_O   = {json.dumps(PRICE_ORIGINAL)};
            const DISC_SEL  = {json.dumps(DISCOUNT_SELECTORS)};
            const IMG_SEL   = {json.dumps(IMG_HOLDER)};

            const getText = (el) => el ? (el.textContent || "").trim() : "";
            const pickFirst = (el, sels) => {{
                for (const s of sels) {{
                    const n = qs(el, s);
                    if (n) return n;
                }}
                return null;
            }};

            const cards = qsa(document, CARD_SEL);
            for (const card of cards) {{
                try {{
                    const brandEl = pickFirst(card, BRAND_SEL);
                    const nameEl  = pickFirst(card, NAME_SEL);
                    const linkEl  = pickFirst(card, LINK_SEL);

                    let discounted = pickFirst(card, PRICE_D);
                    let original   = pickFirst(card, PRICE_O);
                    const discount = pickFirst(card, DISC_SEL);

                    // image lookup: try imgs inside holders first; then background-image
                    let image_url = "";
                    for (const sel of IMG_SEL) {{
                        const container = qs(card, sel) || card;
                        const img = container.querySelector("img, source");
                        if (img) {{
                            image_url = img.getAttribute("src") ||
                                        img.getAttribute("data-src") ||
                                        img.getAttribute("data-lazy") ||
                                        img.getAttribute("srcset") || "";
                            if (image_url) break;
                        }}
                        const style = (container.style && container.style.backgroundImage) || "";
                        if (!image_url && style) {{
                            const m = style.match(/url\\(['"]?(.*?)['"]?\\)/i);
                            if (m) image_url = m[1];
                        }}
                    }}

                    const brand = getText(brandEl);
                    const name  = getText(nameEl);

                    const link  = linkEl ? (linkEl.href || linkEl.getAttribute("href") || "") : "";

                    const discounted_text = discounted ? getText(discounted) : "";
                    const original_text   = original ? getText(original) : "";
                    const discount_text   = discount ? getText(discount) : "";

                    if (name) {{
                        items.push({{
                            brand,
                            name,
                            original_price_text: original_text,
                            discounted_price_text: discounted_text,
                            discount_percent_text: discount_text,
                            product_link: link,
                            image_url,
                            description: `${{brand}} ${{name}}`.trim()
                        }});
                    }}
                }} catch (e) {{
                    // ignore a single card failure
                }}
            }}
            return items;
        }})()
        """
        raw_items: List[Dict[str, Any]] = await page.evaluate(js)

        # Normalize fields
        items: List[Dict[str, Any]] = []
        for it in raw_items:
            link = it.get("product_link", "")
            if link and not link.startswith("http"):
                link = urljoin(base_url, link)

            items.append({
                "brand": (it.get("brand") or "").strip(),
                "name": (it.get("name") or "").strip(),
                "original_price": sanitize_price(it.get("original_price_text", "")) or "",
                "discounted_price": sanitize_price(it.get("discounted_price_text", "")) or "",
                "discount_percent": sanitize_price(it.get("discount_percent_text", "")) or "",
                "product_link": link,
                "image_url": it.get("image_url", ""),
                "description": (it.get("description") or "").strip(),
            })

        return items

    async def save_outputs(self, prefix: str, url: str, products: List[Dict[str, Any]]) -> Dict[str, str]:
        """Save scraped data to multiple formats"""
        out = {}
        ts_str = ts()
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # JSON
        json_path = self.output_dir / uniq_name(prefix, "json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "url": url,
                "timestamp": ts_str,
                "total_products": len(products),
                "products": products
            }, f, indent=2, ensure_ascii=False)
        out["json"] = str(json_path)

        # NDJSON
        ndjson_path = self.output_dir / uniq_name(prefix, "ndjson")
        with open(ndjson_path, "w", encoding="utf-8") as f:
            for p in products:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        out["ndjson"] = str(ndjson_path)

        # CSV
        csv_path = self.output_dir / uniq_name(prefix, "csv")
        cols = ["brand", "name", "original_price", "discounted_price", "discount_percent", "product_link", "image_url", "description"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(products)
        out["csv"] = str(csv_path)

        return out

    async def scrape_once(self, url: str, out_prefix: str, attempt: int) -> List[Dict[str, Any]]:
        """Perform a single scraping attempt"""
        ua = random.choice(USER_AGENTS)
        mobile = "Mobile" in ua or "iPhone" in ua or "Android" in ua
        
        screenshot_file = self.output_dir / uniq_name(f"{out_prefix}_attempt{attempt}", "png")
        products: List[Dict[str, Any]] = []

        log(f"🔄 Attempt {attempt} | UA: {ua}")

        try:
            async with async_playwright() as p:
                browser: Browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                # Prepare context options
                context_options = {
                    "user_agent": ua,
                    "device_scale_factor": 2 if mobile else 1,
                    "is_mobile": mobile,
                    "has_touch": mobile,
                    "ignore_https_errors": True,
                }
                
                # Add viewport if specified
                if mobile:
                    context_options["viewport"] = {"width": 412, "height": 915}
                else:
                    context_options["viewport"] = {"width": 1280, "height": 800}
                
                # Add proxy if configured
                if PROXY.get("server") and PROXY.get("username") and PROXY.get("password"):
                    context_options["proxy"] = {
                        "server": PROXY["server"],
                        "username": PROXY["username"],
                        "password": PROXY["password"]
                    }
                
                context: BrowserContext = await browser.new_context(**context_options)
                page: Page = await context.new_page()
                await self.stealth_patch(page)

                # India geolocation header (Oxylabs)
                await page.set_extra_http_headers(INDIA_GEO_HEADER)

                # Defensive: dismiss dialogs
                page.on("dialog", lambda d: asyncio.create_task(d.dismiss()))

                # Go!
                await page.goto(url, wait_until="domcontentloaded", timeout=180000)
                await asyncio.sleep(randf(2.5, 4.5))
                await self.close_popups(page)

                # Load as much as possible
                await self.load_all_products(page, SCROLL_MAX_PRODUCTS, SCROLL_MAX_MINUTES)

                # Extract
                products = await self.extract_products(page, base_url=url)
                log(f"✅ Extracted {len(products)} products")

                # Screenshot full page
                try:
                    await page.screenshot(path=str(screenshot_file), full_page=True)
                    log(f"📸 Saved screenshot: {screenshot_file}")
                except Exception as e:
                    log(f"❌ Screenshot failed: {e}")

                await context.close()
                await browser.close()

        except Exception as e:
            log(f"❌ Attempt error: {e}")
            logger.exception(f"Detailed error for attempt {attempt}")

        return products

    async def scrape_with_retry(self, url: str, out_prefix: str, max_retries: int = 3) -> Dict[str, Any]:
        """Scrape with retry logic"""
        backoff_s = 4.0
        for attempt in range(1, max_retries + 1):
            products = await self.scrape_once(url, out_prefix, attempt)
            if products:
                outputs = await self.save_outputs(out_prefix, url, products)
                return {
                    "ok": True,
                    "attempt": attempt,
                    "total": len(products),
                    "outputs": outputs
                }
            if attempt < max_retries:
                log("🔁 No data or failed; rotating UA & backing off…")
                await asyncio.sleep(backoff_s + randf(0.0, 2.0))
                backoff_s *= 1.8
        return {"ok": False, "attempt": max_retries, "total": 0, "outputs": {}}

    async def scrape(self, url: Optional[str] = None, output_prefix: Optional[str] = None, max_retries: int = 3) -> Dict[str, Any]:
        """Main scraping method"""
        url = url or URL_DEFAULT
        output_prefix = output_prefix or DEFAULT_PREFIX
        
        log(f"🚀 Starting AJIO scraper for: {url}")
        log(f"📁 Output directory: {self.output_dir.absolute()}")
        
        result = await self.scrape_with_retry(url, output_prefix, max_retries)
        
        if result["ok"]:
            log(f"🎉 Scraping completed successfully!")
            log(f"📊 Total products: {result['total']}")
            log(f"📁 Output files: {result['outputs']}")
        else:
            log(f"❌ Scraping failed after {max_retries} attempts")
            
        return result


def create_argument_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="AJIO Web Scraper - Extract product data from AJIO website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ajio_scraper.py
  python ajio_scraper.py --url "https://www.ajio.com/s/men-shoes"
  python ajio_scraper.py --output-dir ./data --prefix mens_shoes
  python ajio_scraper.py --max-retries 5 --verbose
        """
    )
    
    parser.add_argument(
        "--url", "-u",
        default=URL_DEFAULT,
        help=f"URL to scrape (default: {URL_DEFAULT})"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Output directory for scraped data (default: output)"
    )
    
    parser.add_argument(
        "--prefix", "-p",
        default=DEFAULT_PREFIX,
        help=f"Output file prefix (default: {DEFAULT_PREFIX})"
    )
    
    parser.add_argument(
        "--max-retries", "-r",
        type=int,
        default=3,
        help="Maximum number of retry attempts (default: 3)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser


async def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create scraper instance
    scraper = AjioScraper(output_dir=args.output_dir)
    
    try:
        # Run scraper
        result = await scraper.scrape(
            url=args.url,
            output_prefix=args.prefix,
            max_retries=args.max_retries
        )
        
        # Exit with appropriate code
        sys.exit(0 if result["ok"] else 1)
        
    except KeyboardInterrupt:
        log("🛑 Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        logger.exception("Detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure event loop compatibility across platforms
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
