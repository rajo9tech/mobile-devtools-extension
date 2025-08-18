# AJIO Web Scraper

A desktop-ready web scraper for extracting product data from AJIO.com with proper file organization, configuration management, and cross-platform compatibility.

## Features

- 🚀 **Automated Product Extraction**: Scrapes product details including brand, name, prices, discounts, images, and links
- 🔄 **Smart Scrolling**: Human-like scrolling behavior to load all products with lazy loading support
- 🛡️ **Anti-Detection**: Stealth mode with rotating user agents and proxy support
- 📁 **Multiple Export Formats**: JSON, NDJSON, and CSV output formats
- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux
- ⚙️ **Configurable**: Easy configuration management with environment variables
- 🔧 **CLI Interface**: Command-line interface for easy automation
- 📸 **Debug Support**: Automatic screenshots and comprehensive logging

## Project Structure

```
ajio-scraper/
├── ajio_scraper.py      # Object-oriented scraper class
├── main.py              # Simple main script (your original code enhanced)
├── config.py            # Configuration and settings
├── utils.py             # Utility functions
├── setup.py             # Installation and setup script
├── dependencies.txt     # Python dependencies list
├── .env.example         # Environment variables template
├── run_scraper.bat      # Windows run script
├── run_scraper.sh       # Unix/Linux/macOS run script
├── README.md            # This file
├── output/              # Scraped data output (created automatically)
├── logs/                # Log files (created automatically)
└── screenshots/         # Debug screenshots (created automatically)
```

## Quick Start

### 1. Installation

**Option A: Automated Setup (Recommended)**

For Windows:
```cmd
# Double-click run_scraper.bat or run in Command Prompt
run_scraper.bat
```

For Unix/Linux/macOS:
```bash
# Make executable and run
chmod +x run_scraper.sh
./run_scraper.sh
```

**Option B: Manual Setup**

1. Ensure Python 3.8+ is installed:
```bash
python --version
```

2. Run the setup script:
```bash
python setup.py
```

3. Install dependencies manually (if setup.py fails):
```bash
pip install -r dependencies.txt
playwright install chromium
```

### 2. Configuration

Copy the environment template and configure your settings:
```bash
cp .env.example .env
# Edit .env with your preferred text editor
```

Configure proxy settings in `.env` (optional):
```env
# Proxy Settings (leave empty to scrape without proxy)
OXY_SERVER=http://unblock.oxylabs.io:60000
OXY_USER=your_username_here
OXY_PASS=your_password_here

# Output Configuration
AJIO_OUTPUT_DIR=output
AJIO_MAX_PRODUCTS=4000
AJIO_MAX_MINUTES=10
```

### 3. Basic Usage

**Using the Enhanced Main Script (Recommended for beginners):**
```bash
# Scrape default URL
python main.py

# Scrape specific category
python main.py --url "https://www.ajio.com/s/men-shoes"

# Custom output prefix and retry settings
python main.py --prefix mens_shoes --retries 5
```

**Using the Object-Oriented Scraper:**
```bash
# Basic usage
python ajio_scraper.py

# Advanced usage with custom settings
python ajio_scraper.py --url "https://www.ajio.com/women-clothing" --output-dir ./data --max-retries 5

# Get help with all options
python ajio_scraper.py --help
```

## Usage Examples

### Common Scraping Scenarios

1. **Scrape New Arrivals (Default)**:
```bash
python main.py
```

2. **Scrape Men's Shoes**:
```bash
python main.py --url "https://www.ajio.com/s/men-shoes"
```

3. **Scrape Women's Clothing with Custom Settings**:
```bash
python ajio_scraper.py --url "https://www.ajio.com/women-clothing" --prefix womens_fashion --max-retries 5
```

4. **Scrape Sale Items**:
```bash
python main.py --url "https://www.ajio.com/sale" --prefix sale_items
```

### Output Files

The scraper generates three types of output files in the `output/` directory:

- **JSON** (`.json`): Complete structured data with metadata
- **NDJSON** (`.ndjson`): Newline-delimited JSON for streaming/processing
- **CSV** (`.csv`): Spreadsheet-compatible format

Example output structure:
```json
{
  "url": "https://www.ajio.com/s/newseasondrops-112391",
  "timestamp": "2025-01-18 15:30:45",
  "total_products": 247,
  "products": [
    {
      "brand": "Nike",
      "name": "Air Max Running Shoes",
      "original_price": "5999",
      "discounted_price": "4199",
      "discount_percent": "30",
      "product_link": "https://www.ajio.com/p/...",
      "image_url": "https://assets.ajio.com/...",
      "description": "Nike Air Max Running Shoes"
    }
  ]
}
```

## Advanced Configuration

### Environment Variables

Set these in your `.env` file or system environment:

| Variable | Description | Default |
|----------|-------------|---------|
| `OXY_SERVER` | Proxy server URL | None |
| `OXY_USER` | Proxy username | None |
| `OXY_PASS` | Proxy password | None |
| `AJIO_OUTPUT_DIR` | Output directory | `output` |
| `AJIO_MAX_PRODUCTS` | Maximum products to scrape | `4000` |
| `AJIO_MAX_MINUTES` | Maximum scraping time (minutes) | `10` |

### Customizing Scraper Behavior

Edit `config.py` to modify:
- User agents for different browsers/devices
- CSS selectors for product elements
- Scrolling behavior parameters
- Popup detection and handling
- Output formats and file naming

### Popular AJIO Categories

Common URLs you can use:

```python
categories = {
    "men_clothing": "https://www.ajio.com/men-clothing",
    "women_clothing": "https://www.ajio.com/women-clothing", 
    "kids_clothing": "https://www.ajio.com/kids",
    "shoes": "https://www.ajio.com/shoes",
    "accessories": "https://www.ajio.com/accessories",
    "new_arrivals": "https://www.ajio.com/s/newseasondrops-112391",
    "sale": "https://www.ajio.com/sale",
}
```

## Troubleshooting

### Common Issues

1. **Setup fails**: Ensure Python 3.8+ is installed and internet connection is stable
2. **No products scraped**: Check if the URL is correct and AJIO is accessible
3. **Proxy errors**: Verify proxy credentials in `.env` file
4. **Browser installation fails**: Run `playwright install chromium` manually

### Debug Information

The scraper provides comprehensive logging:
- Console output with timestamps and progress indicators
- Log files in `logs/` directory
- Screenshots in `screenshots/` directory for debugging

### Getting Help

1. Check the console output for error messages
2. Look at the generated log files
3. Verify your URL is a valid AJIO product listing page
4. Ensure dependencies are properly installed

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: At least 4GB RAM recommended
- **Disk Space**: 2GB free space for browser installation and data storage
- **Internet**: Stable broadband connection

## Limitations and Considerations

- **Rate Limiting**: The scraper includes human-like delays to avoid overwhelming the server
- **Legal Compliance**: Ensure your usage complies with AJIO's robots.txt and terms of service
- **Data Accuracy**: Product information may change; verify critical data from the source
- **Maintenance**: Website structure changes may require selector updates in `config.py`

## File Descriptions

### Core Files

- **`main.py`**: Simplified main script based on your original code
- **`ajio_scraper.py`**: Object-oriented scraper with advanced features
- **`config.py`**: All configuration settings and CSS selectors
- **`utils.py`**: Helper functions for logging, data processing, and file operations

### Setup Files

- **`setup.py`**: Automated installation and environment setup
- **`dependencies.txt`**: List of required Python packages
- **`.env.example`**: Template for environment configuration

### Platform Scripts

- **`run_scraper.bat`**: Windows batch script for easy execution
- **`run_scraper.sh`**: Unix/Linux/macOS shell script for easy execution

## License and Disclaimer

This tool is provided for educational and research purposes. Users are responsible for:
- Complying with AJIO's terms of service and robots.txt
- Respecting rate limits and not overwhelming servers
- Using scraped data appropriately and legally
- Understanding that web scraping may have legal implications depending on your jurisdiction and use case

Always ensure your scraping activities are ethical and legal.
