"""
Configuration settings for the Shopping Assistant application.
"""

import os

# E-commerce platforms to scrape
PLATFORMS = {
    "amazon": {
        "base_url": "https://www.amazon.in",
        "search_url": "https://www.amazon.in/s?k={query}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    },
    "flipkart": {
        "base_url": "https://www.flipkart.com",
        "search_url": "https://www.flipkart.com/search?q={query}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    },
}

# Cache settings
CACHE_DIR = "./cache"
CACHE_EXPIRY = 86400  # 24 hours in seconds

# Scraping settings
REQUEST_TIMEOUT = 10  # seconds
REQUEST_DELAY = 1  # seconds between requests
MAX_RETRIES = 3

# Product analysis settings
BUDGET_FLEXIBILITY = 0.1  # Allow products 10% above budget
MIN_REVIEWS = 10  # Minimum number of reviews to consider a product
MAX_PRODUCTS_TO_ANALYZE = 20  # Maximum number of products to analyze per platform
TOP_RECOMMENDATIONS = 5  # Number of top recommendations to return

# Selenium settings (for JavaScript-heavy sites)
HEADLESS = True  # Run browser in headless mode
BROWSER_TIMEOUT = 30  # seconds

# Reddit API settings (for forum reviews)
# To use Reddit API, create an app at https://www.reddit.com/prefs/apps
# and fill in the credentials below
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")  # Your Reddit API client ID
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")  # Your Reddit API client secret
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "python:shopping-assistant:v0.1.0")  # Your Reddit API user agent

# Subreddits to search for product reviews
REDDIT_SUBREDDITS = [
    "gadgets", "tech", "reviews", "BuyItForLife", "GoodValue", 
    "ProductReviews", "electronics", "IndianGaming", "india"
]

# Forum scraping settings
INCLUDE_FORUM_REVIEWS = True  # Whether to include forum reviews in recommendations
MAX_FORUM_REVIEWS = 10  # Maximum number of forum reviews to fetch per product
FORCE_REAL_REDDIT_DATA = True  # Force using real Reddit data when credentials are available
