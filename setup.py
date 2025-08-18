#!/usr/bin/env python3
"""
Setup script for AJIO Web Scraper
Handles installation, dependency management, and environment setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description="Running command"):
    """Execute a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies"""
    requirements = [
        "playwright>=1.40.0",
        "asyncio-throttle>=1.0.2",
    ]
    
    print("📦 Installing Python dependencies...")
    
    for package in requirements:
        result = run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installing {package}"
        )
        if not result:
            return False
    
    return True


def install_playwright_browsers():
    """Install Playwright browser binaries"""
    print("🌐 Installing Playwright browsers...")
    
    # Install Chromium browser
    result = run_command(
        f"{sys.executable} -m playwright install chromium",
        "Installing Chromium browser"
    )
    
    if not result:
        print("⚠️ Browser installation failed. You may need to run this manually:")
        print("python -m playwright install chromium")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    dirs = ["output", "logs", "screenshots"]
    
    print("📁 Creating directories...")
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {path.absolute()}")
    
    return True


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("⚙️ Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file - please edit it with your settings")
    elif not env_file.exists():
        print("⚠️ No .env file found and no template available")
    
    return True


def check_system_requirements():
    """Check system requirements and compatibility"""
    print("🖥️ Checking system requirements...")
    
    system = platform.system()
    print(f"Operating System: {system} {platform.release()}")
    
    # Check available disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        print(f"Free disk space: {free_gb} GB")
        
        if free_gb < 2:
            print("⚠️ Warning: Low disk space. At least 2GB recommended.")
    except Exception as e:
        print(f"⚠️ Could not check disk space: {e}")
    
    return True


def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import asyncio
        from playwright.async_api import async_playwright
        print("✅ All required modules can be imported")
        
        # Test basic functionality
        async def test_playwright():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("data:text/html,<h1>Test</h1>")
                title = await page.title()
                await browser.close()
                return bool(title)
        
        # Run async test
        if asyncio.run(test_playwright()):
            print("✅ Playwright is working correctly")
        else:
            print("❌ Playwright test failed")
            return False
            
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False
    
    return True


def show_usage_instructions():
    """Show usage instructions after successful setup"""
    print("\n" + "="*60)
    print("🎉 AJIO Web Scraper Setup Complete!")
    print("="*60)
    
    print("\n📖 Usage Instructions:")
    print("1. Basic usage:")
    print("   python ajio_scraper.py")
    
    print("\n2. Scrape specific URL:")
    print("   python ajio_scraper.py --url 'https://www.ajio.com/s/men-shoes'")
    
    print("\n3. Custom output directory:")
    print("   python ajio_scraper.py --output-dir ./my_data")
    
    print("\n4. With custom settings:")
    print("   python ajio_scraper.py --max-retries 5 --prefix custom_scrape")
    
    print("\n5. Get help:")
    print("   python ajio_scraper.py --help")
    
    print("\n📁 Files created:")
    print("- output/         : Scraped data files")
    print("- logs/           : Log files")  
    print("- screenshots/    : Debug screenshots")
    print("- .env            : Environment configuration")
    
    print("\n⚙️ Configuration:")
    print("- Edit .env file to set proxy credentials")
    print("- See config.py for advanced settings")
    
    print("\n🚀 Ready to scrape AJIO!")


def main():
    """Main setup function"""
    print("🚀 AJIO Web Scraper Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Installing browsers", install_playwright_browsers),
        ("Creating directories", create_directories),
        ("Setting up environment", create_env_file),
        ("Testing installation", test_installation),
    ]
    
    for description, func in steps:
        print(f"\n🔄 {description}...")
        if not func():
            print(f"❌ Setup failed at: {description}")
            print("Please check the error messages above and try again.")
            sys.exit(1)
    
    # Show success message and instructions
    show_usage_instructions()


if __name__ == "__main__":
    main()
