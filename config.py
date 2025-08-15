"""
Configuration file for AJIO Playwright Scraper
Modify these settings as needed
"""

# Scraping Configuration
SCRAPING_CONFIG = {
    'AJIO_URL': "https://www.ajio.com/s/min-50-percent-off-3348-44441?srsltid=AfmBOoq7Me3ahSZUkzd8rTyKjMw0u5YRCAmQARiSPyJ8mYK0yIvQxijY",
    'OUTPUT_DIR': "output",
    'OUTPUT_FILE_CSV': "ajio_men_grooming_products.csv",
    'OUTPUT_FILE_JSON': "ajio_products.json",
    'SCROLL_PAUSE_TIME': (2, 4),  # min, max seconds
    'MAX_SCROLLS': 50,
    'REQUEST_DELAY': (1, 3)  # min, max seconds between requests
}

# Proxy Configuration (Update with your credentials)
PROXY_CONFIG = {
    'USERNAME': "Techy_46p30",  # Replace with your Oxylabs username
    'PASSWORD': "Techy_20+80=100",  # Replace with your Oxylabs password
    'PROXY_HOST': "pr.oxylabs.io",
    'PROXY_PORT': "7777"
}

# Extended proxy pool for better rotation
PROXY_ENDPOINTS = [
    {"host": "pr.oxylabs.io", "port": "7777", "country": "random"},
    {"host": "us-pr.oxylabs.io", "port": "10000", "country": "us"},
    {"host": "us-pr.oxylabs.io", "port": "10001", "country": "us"},  # sticky session
    {"host": "gb-pr.oxylabs.io", "port": "20000", "country": "gb"},
    {"host": "gb-pr.oxylabs.io", "port": "20001", "country": "gb"},  # sticky session
    {"host": "de-pr.oxylabs.io", "port": "30000", "country": "de"},
    {"host": "fr-pr.oxylabs.io", "port": "40000", "country": "fr"},
    {"host": "ca-pr.oxylabs.io", "port": "50000", "country": "ca"}
]

# Browser Configuration
BROWSER_CONFIG = {
    'HEADLESS': True,  # Set to False for debugging
    'USER_AGENT_ROTATION': True,
    'VIEWPORT_RANDOMIZATION': True,
    'STEALTH_MODE': True
}

# Available viewports for rotation
VIEWPORTS = [
    {'width': 1920, 'height': 1080},  # Full HD
    {'width': 1366, 'height': 768},   # Popular laptop
    {'width': 1440, 'height': 900},   # MacBook
    {'width': 1536, 'height': 864},   # Surface
    {'width': 1280, 'height': 720},   # HD
    {'width': 1600, 'height': 900},   # Wide
]

# Headers rotation pool
HEADERS_ROTATION = [
    {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    },
    {
        'Accept-Language': 'en-GB,en;q=0.8,es;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '0',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate'
    },
    {
        'Accept-Language': 'en-CA,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0'
    }
]
