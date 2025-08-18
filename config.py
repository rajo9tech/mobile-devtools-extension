"""
Configuration settings for AJIO Web Scraper
Contains all constants, selectors, and configurable parameters.
"""

import os
from typing import List, Dict, Tuple

# Default URL to scrape
URL_DEFAULT = "https://www.ajio.com/s/newseasondrops-112391"

# ---------- Browser Configuration ---------- #

USER_AGENTS = [
    # Mobile (fresh-ish)
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/637.36",
]

# Geographic headers for targeting India
INDIA_GEO_HEADER = {"x-oxylabs-geo-location": "India"}

# ---------- Proxy Configuration ---------- #

# Proxy settings (environment variables take precedence)
PROXY = {
    "server": os.getenv("OXY_SERVER", "http://unblock.oxylabs.io:60000"),
    "username": os.getenv("OXY_USER", "Techy_46p3O"),
    "password": os.getenv("OXY_PASS", "Techy_20+80=100"),
}

# ---------- Popup Management ---------- #

# Selectors for detecting popups
POPUP_SELECTORS = [
    "div#popup.ZHLvX._1z3ys",             # AJIO specific popup
    "div#growlDiv",                        # generic growl/modal
    "div#loginSignupModal",                # login/signup modal
    "div.newsletter-modal, div[data-testid='newsletter-modal']",
    "div.cookie, div#cookie, div[id*='cookie']",
    "div[role='dialog']",
]

# Selectors for closing popups
POPUP_CLOSE_SELECTORS = [
    "div#popup_close",
    "button[aria-label='Close']",
    "button:has-text('Close')",
    "button:has-text('No, thanks')",
    "button[aria-label='close'], [data-action='close'], .close, .ic-close",
    "button:has-text('✕'), .modal-close, .cross-icon",
]

# ---------- Scrolling Configuration ---------- #

# Maximum products to load (safety cap)
SCROLL_MAX_PRODUCTS = 4000

# Maximum time to spend scrolling (minutes)
SCROLL_MAX_MINUTES = 10.0

# Human-like scrolling parameters
SCROLL_HUMAN_STEP_MIN = 0.6               # x viewport height
SCROLL_HUMAN_STEP_MAX = 2.8               # x viewport height
SCROLL_WAIT_MIN_S = 1.2                   # minimum wait between scrolls
SCROLL_WAIT_MAX_S = 3.3                   # maximum wait between scrolls
SCROLL_IDLE_PINGS = (6, 10)               # idle time range (seconds)
SCROLL_UPWARDS_CHANCE = 0.12              # probability of scrolling upwards
SCROLL_MOUSE_WIGGLE_CHANCE = 0.25         # probability of mouse movement

# ---------- DOM Growth Detection ---------- #

# Number of stalled cycles before switching strategy
DOM_GROWTH_STALL_REPEATS = 6

# Wait time for DOM growth detection
DOM_GROWTH_AWAIT_S = (2.5, 5.0)

# Fallback scrolling parameters
FALLBACK_BOTTOM_SCROLL_ROUNDS = 35        # max scroll-to-bottom rounds
BOTTOM_STABLE_REPEATS = 6                 # stable height checks before stopping

# ---------- Product Extraction Selectors ---------- #

# Main product card selector
CARD_SELECTOR = "div.item.rilrtl-products-list__item.item, li.rilrtl-products-list__item, div[data-testid='product-card']"

# Product link selector
LINK_SELECTOR = "a.rilrtl-products-list__link, a[href*='/p/'], a[href*='/s/']"

# Brand name selectors (in priority order)
BRAND_SELECTORS = [
    ".brand strong", 
    ".brand", 
    "[data-testid='brandName']"
]

# Product name selectors
NAME_SELECTORS = [
    ".name", 
    ".item-name", 
    "[id^='product-title-']", 
    "[data-testid='productTitle']"
]

# Price selectors
PRICE_DISCOUNTED = [
    "#price-value", 
    ".price-value", 
    "[data-testid='price']", 
    ".price .price"
]

PRICE_ORIGINAL = [
    ".orginal-price", 
    ".price-original", 
    "[data-testid='originalPrice']", 
    ".price .mrp"
]

# Discount percentage selectors
DISCOUNT_SELECTORS = [
    ".discount", 
    "[data-testid='discount']", 
    ".offer-price .discount"
]

# Image container selectors
IMG_HOLDER = [
    ".imgHolder", 
    "[data-testid='imageHolder']", 
    ".image-rlp, .img-block, picture, img"
]

# ---------- File Output Configuration ---------- #

# Default prefix for output files
DEFAULT_PREFIX = "ajio_scrape"

# Supported output formats
OUTPUT_FORMATS = ["json", "ndjson", "csv"]

# ---------- Alternative URLs ---------- #

# Common AJIO category URLs for testing
CATEGORY_URLS = {
    "men_clothing": "https://www.ajio.com/men-clothing",
    "women_clothing": "https://www.ajio.com/women-clothing", 
    "kids_clothing": "https://www.ajio.com/kids",
    "shoes": "https://www.ajio.com/shoes",
    "accessories": "https://www.ajio.com/accessories",
    "new_arrivals": "https://www.ajio.com/s/newseasondrops-112391",
    "sale": "https://www.ajio.com/sale",
}

# ---------- Environment Variable Names ---------- #

ENV_VARS = {
    "proxy_server": "OXY_SERVER",
    "proxy_user": "OXY_USER", 
    "proxy_pass": "OXY_PASS",
    "output_dir": "AJIO_OUTPUT_DIR",
    "max_products": "AJIO_MAX_PRODUCTS",
    "max_minutes": "AJIO_MAX_MINUTES",
}

# ---------- Error Handling Configuration ---------- #

# Retry configuration
DEFAULT_MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 4.0
RETRY_BACKOFF_MULTIPLIER = 1.8

# Timeout settings (milliseconds)
PAGE_LOAD_TIMEOUT = 180000
POPUP_CLOSE_TIMEOUT = 1000
NETWORK_IDLE_TIMEOUT = 4000
