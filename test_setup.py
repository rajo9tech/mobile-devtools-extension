#!/usr/bin/env python3
"""
Demo script to test the AJIO Playwright Scraper
This is a simplified version for testing purposes
"""

import asyncio
from playwright.async_api import async_playwright

async def test_connection():
    """Test basic Playwright functionality"""
    print("🧪 Testing Playwright setup...")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Test basic navigation
        await page.goto("https://httpbin.org/ip")
        content = await page.content()

        if "origin" in content:
            print("✅ Playwright is working correctly!")
        else:
            print("❌ Playwright test failed")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
