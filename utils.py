"""
Utility functions for AJIO Web Scraper
Contains helper functions for logging, file operations, and data processing.
"""

import re
import time
import random
import string
from typing import Union


def ts() -> str:
    """Get current timestamp as formatted string"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    """Simple logging function with timestamp"""
    print(f"[{ts()}] {msg}", flush=True)


def randf(a: float, b: float) -> float:
    """Generate random float between a and b"""
    return random.uniform(a, b)


def randbool(p: float) -> bool:
    """Generate random boolean with probability p"""
    return random.random() < p


def sanitize_price(text: str) -> str:
    """
    Extract numeric digits from price text
    
    Args:
        text: Raw price text (e.g., "₹1,299", "$29.99")
        
    Returns:
        String containing only digits (e.g., "1299", "2999")
    """
    if not text:
        return ""
    digits = re.sub(r"[^0-9]", "", text)
    return digits


def uniq_name(prefix: str, ext: str) -> str:
    """
    Generate unique filename with timestamp and random salt
    
    Args:
        prefix: File prefix
        ext: File extension (without dot)
        
    Returns:
        Unique filename string
    """
    salt = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}_{salt}.{ext}"


def format_price(price_str: str) -> str:
    """
    Format price string for display
    
    Args:
        price_str: Raw price digits
        
    Returns:
        Formatted price string
    """
    if not price_str:
        return ""
    
    # Add currency symbol and formatting
    try:
        price_int = int(price_str)
        return f"₹{price_int:,}"
    except ValueError:
        return price_str


def validate_url(url: str) -> bool:
    """
    Validate if URL is a proper AJIO URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid AJIO URL, False otherwise
    """
    if not url:
        return False
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Check if it's an AJIO domain
    return 'ajio.com' in url.lower()


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = ' '.join(text.split())
    
    # Remove common artifacts
    cleaned = re.sub(r'[^\w\s\-.,!?()&%]', '', cleaned)
    
    return cleaned.strip()


def parse_discount(discount_text: str) -> Union[int, None]:
    """
    Parse discount percentage from text
    
    Args:
        discount_text: Raw discount text (e.g., "50% OFF", "(60% OFF)")
        
    Returns:
        Discount percentage as integer, or None if not found
    """
    if not discount_text:
        return None
    
    # Extract percentage number
    match = re.search(r'(\d+)%', discount_text)
    if match:
        return int(match.group(1))
    
    return None


def safe_filename(filename: str) -> str:
    """
    Create safe filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename for filesystem
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe = re.sub(r'\s+', '_', safe)
    safe = safe.strip('._')
    
    return safe[:100] if safe else "unnamed"  # Limit length


def estimate_completion_time(current_count: int, target_count: int, start_time: float) -> str:
    """
    Estimate completion time based on current progress
    
    Args:
        current_count: Current number of items processed
        target_count: Target number of items
        start_time: Start timestamp
        
    Returns:
        Formatted ETA string
    """
    if current_count <= 0:
        return "Unknown"
    
    elapsed = time.time() - start_time
    rate = current_count / elapsed  # items per second
    
    if rate <= 0:
        return "Unknown"
    
    remaining = target_count - current_count
    eta_seconds = remaining / rate
    
    if eta_seconds < 60:
        return f"{eta_seconds:.0f}s"
    elif eta_seconds < 3600:
        return f"{eta_seconds/60:.1f}m"
    else:
        return f"{eta_seconds/3600:.1f}h"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def get_random_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> float:
    """
    Get random delay for rate limiting
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Random delay value
    """
    return random.uniform(min_delay, max_delay)


def progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Generate ASCII progress bar
    
    Args:
        current: Current progress value
        total: Total/target value
        width: Width of progress bar in characters
        
    Returns:
        Formatted progress bar string
    """
    if total <= 0:
        return "[" + "?" * width + "]"
    
    percentage = min(current / total, 1.0)
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    
    return f"[{bar}] {percentage*100:.1f}%"
