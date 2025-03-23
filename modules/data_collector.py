"""
Data collector module for the Shopping Assistant application.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils.logger import logger
from ..utils.exceptions import ScrapingError, CacheError
from ..utils.helpers import generate_cache_key, get_cached_data, save_to_cache
from .mock_data_provider import MockDataProvider
from .forum_scraper import RedditScraper

class DataCollector:
    """
    Collects and aggregates data from multiple sources.
    """
    
    def __init__(self, scraper, config):
        """
        Initialize the DataCollector.
        
        Args:
            scraper: WebScraper instance
            config: Configuration settings
        """
        self.scraper = scraper
        self.config = config
        self.cache_dir = config.CACHE_DIR
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize mock data provider for fallback
        self.mock_data_provider = MockDataProvider()
        
        # Initialize Reddit scraper for forum reviews
        self.reddit_scraper = RedditScraper(config)
        
    def collect_data(self, queries):
        """
        Collect data from multiple sources based on queries.
        
        Args:
            queries: Dictionary of platform-specific queries
            
        Returns:
            dict: Collected data
        """
        logger.info("Collecting data from multiple sources")
        
        all_products = []
        
        # Collect data from Amazon
        amazon_products = self._collect_from_platform("amazon", queries["amazon"]["combined"])
        if amazon_products:
            all_products.extend(amazon_products)
            
        # Collect data from Flipkart
        flipkart_products = self._collect_from_platform("flipkart", queries["flipkart"]["combined"])
        if flipkart_products:
            all_products.extend(flipkart_products)
            
        logger.info(f"Collected {len(all_products)} products in total")
        
        return {
            "products": all_products,
            "sources": ["amazon", "flipkart"]
        }
        
    def _collect_from_platform(self, platform, query):
        """
        Collect data from a specific platform.
        
        Args:
            platform: Platform name
            query: Search query
            
        Returns:
            list: Product data
        """
        logger.info(f"Collecting data from {platform} with query: {query}")
        
        # Extract product type and budget from query
        # Example query: "laptop under 50000 gaming lightweight"
        query_parts = query.lower().split()
        product_type = query_parts[0] if query_parts else ""
        budget = 50000  # Default budget
        
        # Try to extract budget from query
        for i, part in enumerate(query_parts):
            if part == "under" and i + 1 < len(query_parts):
                try:
                    budget = float(query_parts[i + 1])
                except ValueError:
                    pass
        
        # Extract preferences from query
        preferences = []
        for part in query_parts[2:]:  # Skip product type and budget
            if part not in ["under", str(budget)]:
                preferences.append(part)
        
        # Generate cache key
        cache_key = generate_cache_key(query, platform)
        
        # Check cache first
        cached_data = get_cached_data(
            cache_key, 
            self.cache_dir, 
            self.config.CACHE_EXPIRY
        )
        
        if cached_data:
            logger.info(f"Using cached data for {platform}")
            return cached_data
            
        # If not in cache, scrape data
        try:
            products = []
            
            if platform == "amazon":
                products = self.scraper.scrape_amazon(query)
            elif platform == "flipkart":
                products = self.scraper.scrape_flipkart(query)
            else:
                logger.warning(f"Unsupported platform: {platform}")
                return []
                
            # Normalize data
            normalized_products = self._normalize_data(products, platform)
            
            # If no products found from scraping, use mock data
            if not normalized_products:
                logger.info(f"No products found from {platform}, using mock data")
                mock_products = self.mock_data_provider.get_products(product_type, budget, preferences)
                # Filter mock products by platform
                mock_products = [p for p in mock_products if p['platform'].lower() == platform.lower()]
                normalized_products = mock_products
            
            # Save to cache
            save_to_cache(normalized_products, cache_key, self.cache_dir)
            
            return normalized_products
            
        except ScrapingError as e:
            logger.error(f"Error collecting data from {platform}: {str(e)}")
            logger.info(f"Using mock data for {platform} due to scraping error")
            
            # Use mock data as fallback
            mock_products = self.mock_data_provider.get_products(product_type, budget, preferences)
            # Filter mock products by platform
            mock_products = [p for p in mock_products if p['platform'].lower() == platform.lower()]
            
            # Save to cache
            save_to_cache(mock_products, cache_key, self.cache_dir)
            
            return mock_products
            
    def _normalize_data(self, products, platform):
        """
        Normalize data from different platforms to a common format.
        
        Args:
            products: List of product data
            platform: Platform name
            
        Returns:
            list: Normalized product data
        """
        normalized = []
        
        for product in products:
            # Skip products without essential data
            if not product.get('name') or not product.get('price'):
                continue
                
            # Ensure all required fields are present
            normalized_product = {
                'name': product.get('name', ''),
                'url': product.get('url', ''),
                'price': product.get('price', 0),
                'price_text': product.get('price_text', ''),
                'rating': product.get('rating', None),
                'review_count': product.get('review_count', 0),
                'features': product.get('features', []),
                'image_url': product.get('image_url', ''),
                'platform': platform
            }
            
            normalized.append(normalized_product)
            
        return normalized
        
    def collect_reviews(self, products, max_products=5):
        """
        Collect reviews for top products.
        
        Args:
            products: List of products
            max_products: Maximum number of products to collect reviews for
            
        Returns:
            dict: Products with reviews
        """
        logger.info(f"Collecting reviews for top {max_products} products")
        
        # Select top products to collect reviews for
        top_products = products[:max_products]
        
        # Use ThreadPoolExecutor for parallel review collection
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Create a future for each product
            future_to_product = {
                executor.submit(self._collect_product_reviews, product): product
                for product in top_products
            }
            
            # Process results as they complete
            for future in as_completed(future_to_product):
                product = future_to_product[future]
                try:
                    # Get the result (product with reviews)
                    product_with_reviews = future.result()
                    # Update the product in the list
                    index = top_products.index(product)
                    top_products[index] = product_with_reviews
                except Exception as e:
                    logger.error(f"Error collecting reviews for {product.get('name')}: {str(e)}")
                    
        return top_products
        
    def _collect_product_reviews(self, product):
        """
        Collect reviews for a specific product.
        
        Args:
            product: Product data
            
        Returns:
            dict: Product data with reviews
        """
        platform = product.get('platform')
        url = product.get('url')
        product_name = product.get('name', '')
        
        if not platform or not url or not product_name:
            return product
            
        # Generate cache key for e-commerce reviews
        ecommerce_cache_key = generate_cache_key(f"reviews_{url}", platform)
        
        # Check cache first for e-commerce reviews
        cached_ecommerce_reviews = get_cached_data(
            ecommerce_cache_key, 
            self.cache_dir, 
            self.config.CACHE_EXPIRY
        )
        
        # Generate cache key for forum reviews
        forum_cache_key = generate_cache_key(f"forum_reviews_{product_name}", "reddit")
        
        # Check cache for forum reviews
        cached_forum_reviews = get_cached_data(
            forum_cache_key, 
            self.cache_dir, 
            self.config.CACHE_EXPIRY
        )
        
        # If both are cached, combine and return
        if cached_ecommerce_reviews and cached_forum_reviews and hasattr(self.config, 'INCLUDE_FORUM_REVIEWS') and self.config.INCLUDE_FORUM_REVIEWS:
            logger.info(f"Using cached reviews for {product_name}")
            product['reviews'] = cached_ecommerce_reviews
            product['forum_reviews'] = cached_forum_reviews
            return product
        elif cached_ecommerce_reviews:
            logger.info(f"Using cached e-commerce reviews for {product_name}")
            product['reviews'] = cached_ecommerce_reviews
            # Still need to get forum reviews if enabled
        
        # Collect e-commerce reviews if not cached
        ecommerce_reviews = []
        if not cached_ecommerce_reviews:
            try:
                ecommerce_reviews = self.scraper.scrape_reviews(url, platform)
                
                # If no reviews found, generate mock reviews
                if not ecommerce_reviews:
                    logger.info(f"No e-commerce reviews found for {product_name}, generating mock reviews")
                    ecommerce_reviews = self._generate_mock_reviews(product)
                
                # Save to cache
                save_to_cache(ecommerce_reviews, ecommerce_cache_key, self.cache_dir)
                
            except Exception as e:
                logger.error(f"Error collecting e-commerce reviews for {product_name}: {str(e)}")
                logger.info(f"Generating mock reviews for {product_name}")
                
                # Generate mock reviews
                ecommerce_reviews = self._generate_mock_reviews(product)
                
                # Save to cache
                save_to_cache(ecommerce_reviews, ecommerce_cache_key, self.cache_dir)
        else:
            ecommerce_reviews = cached_ecommerce_reviews
            
        # Add e-commerce reviews to product
        product['reviews'] = ecommerce_reviews
        
        # Always collect forum reviews when enabled
        include_forum_reviews = hasattr(self.config, 'INCLUDE_FORUM_REVIEWS') and self.config.INCLUDE_FORUM_REVIEWS
        if include_forum_reviews:
            forum_reviews = []
            if not cached_forum_reviews:
                try:
                    # Collect forum reviews
                    forum_reviews = self._collect_forum_reviews(product_name, platform)
                    
                    # Save to cache
                    save_to_cache(forum_reviews, forum_cache_key, self.cache_dir)
                    
                except Exception as e:
                    logger.error(f"Error collecting forum reviews for {product_name}: {str(e)}")
                    forum_reviews = []
            else:
                forum_reviews = cached_forum_reviews
                
            # Add forum reviews to product
            product['forum_reviews'] = forum_reviews
            
            # Log the number of forum reviews collected
            logger.info(f"Added {len(forum_reviews)} forum reviews for {product_name}")
            
        return product
        
    def _collect_forum_reviews(self, product_name, platform=None):
        """
        Collect reviews for a product from forums.
        
        Args:
            product_name: Name of the product
            platform: Optional platform to filter by
            
        Returns:
            list: Review data from forums
        """
        logger.info(f"Collecting forum reviews for {product_name} from Reddit")
        
        # Log Reddit configuration
        if hasattr(self.config, 'REDDIT_CLIENT_ID'):
            logger.info(f"Reddit API credentials configured: {bool(self.config.REDDIT_CLIENT_ID)}")
        if hasattr(self.config, 'FORCE_REAL_REDDIT_DATA'):
            logger.info(f"Force real Reddit data: {self.config.FORCE_REAL_REDDIT_DATA}")
        
        try:
            # Get reviews from Reddit
            logger.info(f"Calling Reddit scraper for {product_name}")
            reddit_reviews = self.reddit_scraper.scrape_reviews(product_name, platform)
            
            # Limit the number of reviews
            max_reviews = self.config.MAX_FORUM_REVIEWS if hasattr(self.config, 'MAX_FORUM_REVIEWS') else 10
            if len(reddit_reviews) > max_reviews:
                reddit_reviews = reddit_reviews[:max_reviews]
                
            logger.info(f"Collected {len(reddit_reviews)} forum reviews for {product_name}")
            
            # Log some details about the reviews
            if reddit_reviews:
                logger.info(f"First review: {reddit_reviews[0].get('text', '')[:50]}...")
            
            return reddit_reviews
            
        except Exception as e:
            logger.error(f"Error collecting forum reviews for {product_name}: {str(e)}")
            return []
            
    def _generate_mock_reviews(self, product):
        """
        Generate mock reviews for a product.
        
        Args:
            product: Product data
            
        Returns:
            list: Mock review data
        """
        import random
        from datetime import datetime, timedelta
        
        # Get product rating or generate a random one
        product_rating = product.get('rating', random.uniform(3.5, 4.8))
        
        # Generate 3-5 mock reviews
        num_reviews = random.randint(3, 5)
        reviews = []
        
        # Common positive adjectives
        positive_adjectives = [
            "excellent", "amazing", "fantastic", "great", "good", 
            "wonderful", "outstanding", "superb", "impressive", "solid"
        ]
        
        # Common negative adjectives
        negative_adjectives = [
            "disappointing", "poor", "mediocre", "subpar", "average",
            "underwhelming", "frustrating", "lacking", "inadequate", "flawed"
        ]
        
        # Common review titles
        positive_titles = [
            "Great purchase!", "Highly recommended", "Excellent product", 
            "Very satisfied", "Worth every penny", "Exceeded expectations"
        ]
        
        negative_titles = [
            "Not worth it", "Disappointed", "Save your money", 
            "Not as advertised", "Wouldn't recommend", "Mediocre at best"
        ]
        
        # Product features to mention in reviews
        features = product.get('features', [])
        if not features:
            features = ["quality", "design", "performance", "value", "durability"]
        
        # Generate reviews
        for i in range(num_reviews):
            # Determine if this is a positive or negative review
            # More positive reviews for higher-rated products
            is_positive = random.random() < (product_rating / 5.0)
            
            # Generate rating (positive: 4-5, negative: 1-3)
            if is_positive:
                rating = random.randint(4, 5)
                adjectives = positive_adjectives
                titles = positive_titles
            else:
                rating = random.randint(1, 3)
                adjectives = negative_adjectives
                titles = negative_titles
            
            # Generate review date (within last 3 months)
            days_ago = random.randint(1, 90)
            review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%B %d, %Y")
            
            # Generate review title
            title = random.choice(titles)
            
            # Generate review text
            text = ""
            
            # Add opening sentence
            if is_positive:
                text += f"I {random.choice(['really like', 'love', 'am very happy with', 'am impressed by'])} this {product.get('name', 'product')}. "
            else:
                text += f"I {random.choice(['am disappointed with', 'regret buying', 'am not satisfied with', 'expected more from'])} this {product.get('name', 'product')}. "
            
            # Add 1-2 sentences about features
            for _ in range(random.randint(1, 2)):
                if features:
                    feature = random.choice(features)
                    adjective = random.choice(adjectives)
                    text += f"The {feature} is {adjective}. "
            
            # Add closing sentence
            if is_positive:
                text += random.choice([
                    "Would definitely recommend!",
                    "Very happy with my purchase.",
                    "Great value for money.",
                    "One of the best purchases I've made."
                ])
            else:
                text += random.choice([
                    "Would not recommend.",
                    "Not worth the price.",
                    "Look elsewhere for better options.",
                    "Quite disappointed overall."
                ])
            
            # Create review
            review = {
                'rating': rating,
                'title': title,
                'text': text,
                'date': review_date
            }
            
            reviews.append(review)
        
        return reviews
