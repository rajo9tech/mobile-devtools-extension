#!/usr/bin/env python3
"""
Setup script for AJIO Playwright Scraper
This script installs all required dependencies
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 Setting up AJIO Playwright Scraper...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python version: {sys.version}")

    # Install pip packages
    print("📦 Installing Python packages...")
    run_command("pip install -r requirements.txt")

    # Install Playwright browsers
    print("🌐 Installing Playwright browsers...")
    run_command("playwright install chromium")

    # Create output directory
    if not os.path.exists("output"):
        os.makedirs("output")
        print("✅ Created output directory")

    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your Oxylabs credentials in config.py")
    print("2. Run the scraper with: python ajio_playwright_scraper.py")

if __name__ == "__main__":
    main()
