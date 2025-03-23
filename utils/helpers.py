"""
Helper functions for the Shopping Assistant application.
"""

import re
import json
import os
import time
import hashlib
from datetime import datetime, timedelta

from .logger import logger
from .exceptions import CacheError

def sanitize_query(query):
    """
    Sanitize a search query by removing special characters and normalizing whitespace.
    
    Args:
        query: The search query to sanitize
        
    Returns:
        str: Sanitized query
    """
    # Replace special characters with spaces
    sanitized = re.sub(r'[^\w\s]', ' ', query)
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

def extract_price(price_str):
    """
    Extract a numeric price from a string.
    
    Args:
        price_str: String containing a price (e.g., "₹1,499.00")
        
    Returns:
        float: Extracted price as a float
    """
    if not price_str:
        return None
        
    # Extract digits and decimal point
    price_match = re.search(r'[\d,]+\.?\d*', price_str)
    if not price_match:
        return None
        
    # Remove commas and convert to float
    price = price_match.group().replace(',', '')
    try:
        return float(price)
    except ValueError:
        return None

def generate_cache_key(query, platform):
    """
    Generate a unique cache key for a query and platform.
    
    Args:
        query: Search query
        platform: Platform name
        
    Returns:
        str: Cache key
    """
    # Create a string to hash
    key_string = f"{platform}:{query}".lower()
    # Generate MD5 hash
    return hashlib.md5(key_string.encode()).hexdigest()

def get_cached_data(cache_key, cache_dir, expiry_seconds=86400):
    """
    Retrieve data from cache if it exists and is not expired.
    
    Args:
        cache_key: Cache key
        cache_dir: Cache directory
        expiry_seconds: Cache expiry time in seconds
        
    Returns:
        dict or None: Cached data or None if not found or expired
    """
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    # Check if cache file exists
    if not os.path.exists(cache_file):
        return None
        
    try:
        # Read cache file
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired
        timestamp = cache_data.get('timestamp')
        if not timestamp:
            return None
            
        cache_time = datetime.fromisoformat(timestamp)
        if datetime.now() - cache_time > timedelta(seconds=expiry_seconds):
            logger.debug(f"Cache expired for key: {cache_key}")
            return None
            
        logger.debug(f"Cache hit for key: {cache_key}")
        return cache_data.get('data')
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading cache: {str(e)}")
        return None

def save_to_cache(data, cache_key, cache_dir):
    """
    Save data to cache.
    
    Args:
        data: Data to cache
        cache_key: Cache key
        cache_dir: Cache directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    try:
        # Create cache data structure
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Write to cache file
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        logger.debug(f"Data saved to cache: {cache_key}")
        return True
        
    except IOError as e:
        logger.error(f"Error saving to cache: {str(e)}")
        raise CacheError(f"Failed to save data to cache: {str(e)}")

def format_currency(amount):
    """
    Format a number as Indian Rupees.
    
    Args:
        amount: Amount to format
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "N/A"
        
    # Format with Indian numbering system (2 decimal places)
    # For example: 1,00,000.00
    x, y = str(round(float(amount), 2)).split('.')
    x = x.replace(',', '')
    lastthree = x[-3:]
    other = x[:-3]
    if other:
        formatted = ''.join([other[i-2:i] + ',' for i in range(len(other), 0, -2)])
        formatted = formatted + lastthree
    else:
        formatted = lastthree
    formatted = formatted + '.' + y.ljust(2, '0')
    
    return f"₹{formatted}"

def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Backoff factor
        
    Returns:
        Result of the function call
    """
    retries = 0
    delay = initial_delay
    
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                raise
                
            logger.warning(f"Retry {retries}/{max_retries} after error: {str(e)}")
            time.sleep(delay)
            delay *= backoff_factor
