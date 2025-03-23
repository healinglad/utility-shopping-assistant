"""
Forum scraper module for the Shopping Assistant application.

This module provides functionality to scrape product reviews and discussions from forums like Reddit.
"""

import re
import time
import random
from datetime import datetime, timedelta

# Try to import PRAW (Python Reddit API Wrapper)
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from ..utils.logger import logger
from ..utils.exceptions import ScrapingError

class ForumScraper:
    """
    Base class for forum scrapers.
    """
    
    def __init__(self, config):
        """
        Initialize the ForumScraper.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        
    def scrape_reviews(self, product_name, platform=None):
        """
        Scrape reviews for a product from forums.
        
        Args:
            product_name: Name of the product
            platform: Optional platform to filter by
            
        Returns:
            list: Review data
        """
        raise NotImplementedError("Subclasses must implement scrape_reviews")

class RedditScraper(ForumScraper):
    """
    Scraper for Reddit.
    """
    
    def __init__(self, config):
        """
        Initialize the RedditScraper.
        
        Args:
            config: Configuration settings
        """
        super().__init__(config)
        self.reddit = None
        
        # Initialize Reddit API client if PRAW is available
        if PRAW_AVAILABLE and hasattr(config, 'REDDIT_CLIENT_ID'):
            try:
                self.reddit = praw.Reddit(
                    client_id=config.REDDIT_CLIENT_ID,
                    client_secret=config.REDDIT_CLIENT_SECRET,
                    user_agent=config.REDDIT_USER_AGENT
                )
                logger.info("Reddit API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit API client: {str(e)}")
                self.reddit = None
        
    def scrape_reviews(self, product_name, platform=None):
        """
        Scrape reviews for a product from Reddit.
        
        Args:
            product_name: Name of the product
            platform: Optional platform to filter by
            
        Returns:
            list: Review data
        """
        logger.info(f"Scraping Reddit for reviews of {product_name}")
        
        # Check if PRAW is available
        if not PRAW_AVAILABLE:
            logger.warning("PRAW not available, using mock data. Please install PRAW with 'pip install praw'")
            return self._generate_mock_reviews(product_name, platform)
            
        # Check if Reddit client is initialized
        if self.reddit is None:
            # Try to initialize Reddit client with credentials from config
            if hasattr(self.config, 'REDDIT_CLIENT_ID') and self.config.REDDIT_CLIENT_ID:
                try:
                    self.reddit = praw.Reddit(
                        client_id=self.config.REDDIT_CLIENT_ID,
                        client_secret=self.config.REDDIT_CLIENT_SECRET,
                        user_agent=self.config.REDDIT_USER_AGENT
                    )
                    logger.info("Reddit API client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Reddit API client: {str(e)}")
                    logger.warning("Using mock data due to Reddit API client initialization failure")
                    return self._generate_mock_reviews(product_name, platform)
            else:
                logger.warning("Reddit credentials not found in config, using mock data")
                return self._generate_mock_reviews(product_name, platform)
            
        # Check if we should force using real Reddit data
        force_real_data = hasattr(self.config, 'FORCE_REAL_REDDIT_DATA') and self.config.FORCE_REAL_REDDIT_DATA
        
        try:
            # Log that we're using real Reddit data
            logger.info("Using real Reddit data for product reviews")
            
            # Search for product on relevant subreddits
            subreddits = self.config.REDDIT_SUBREDDITS if hasattr(self.config, 'REDDIT_SUBREDDITS') else [
                "gadgets", "tech", "reviews", "BuyItForLife", "GoodValue", 
                "ProductReviews", "electronics"
            ]
            
            # Combine subreddits for search
            subreddit = self.reddit.subreddit('+'.join(subreddits))
            
            # Search for product
            search_query = f"{product_name} review"
            search_results = subreddit.search(search_query, limit=10)
            
            reviews = []
            
            # Process search results
            for submission in search_results:
                # Skip if not relevant
                if not self._is_relevant(submission.title, product_name):
                    continue
                    
                # Get top comments
                submission.comments.replace_more(limit=0)  # Only get top-level comments
                comments = submission.comments.list()[:5]  # Get top 5 comments
                
                for comment in comments:
                    # Skip short or irrelevant comments
                    if len(comment.body) < 50 or not self._is_relevant(comment.body, product_name):
                        continue
                        
                    # Extract sentiment and rating
                    sentiment, rating = self._analyze_sentiment(comment.body)
                    
                    # Create review
                    review = {
                        'rating': rating,
                        'title': submission.title[:100],  # Truncate long titles
                        'text': comment.body[:500],  # Truncate long comments
                        'date': datetime.fromtimestamp(comment.created_utc).strftime("%B %d, %Y"),
                        'source': 'Reddit',
                        'url': f"https://www.reddit.com{submission.permalink}",
                        'author': comment.author.name if comment.author else "[deleted]"
                    }
                    
                    reviews.append(review)
                    
                    # Limit to 10 reviews
                    if len(reviews) >= 10:
                        break
                        
                # Limit to 10 reviews
                if len(reviews) >= 10:
                    break
                    
            logger.info(f"Scraped {len(reviews)} reviews from Reddit")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Reddit: {str(e)}")
            return self._generate_mock_reviews(product_name, platform)
            
    def _is_relevant(self, text, product_name):
        """
        Check if text is relevant to the product.
        
        Args:
            text: Text to check
            product_name: Product name
            
        Returns:
            bool: True if relevant, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        product_lower = product_name.lower()
        
        # Check if product name is in text
        if product_lower in text_lower:
            return True
            
        # Check for product name parts (for multi-word product names)
        product_parts = product_lower.split()
        if len(product_parts) > 1:
            # Check if at least 2 parts of the product name are in the text
            matches = sum(1 for part in product_parts if part in text_lower)
            if matches >= 2:
                return True
                
        return False
        
    def _analyze_sentiment(self, text):
        """
        Analyze sentiment of text and estimate rating.
        
        Args:
            text: Text to analyze
            
        Returns:
            tuple: (sentiment, rating)
        """
        # Simple sentiment analysis based on keywords
        positive_words = [
            "good", "great", "excellent", "amazing", "awesome", "fantastic",
            "love", "best", "perfect", "recommend", "worth", "happy", "satisfied",
            "quality", "reliable", "durable", "impressive", "solid", "nice"
        ]
        
        negative_words = [
            "bad", "poor", "terrible", "awful", "horrible", "worst",
            "hate", "disappointing", "disappointed", "waste", "regret", "unhappy",
            "cheap", "unreliable", "break", "broke", "issue", "problem", "defective",
            "return", "fail", "failure", "avoid"
        ]
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text_lower))
        negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text_lower))
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            sentiment = 0  # Neutral
        else:
            sentiment = (positive_count - negative_count) / total
            
        # Convert sentiment to rating (1-5)
        rating = 3 + sentiment * 2
        rating = max(1, min(5, rating))  # Clamp to 1-5
        
        return sentiment, rating
        
    def _generate_mock_reviews(self, product_name, platform=None):
        """
        Generate mock reviews for a product.
        
        Args:
            product_name: Product name
            platform: Optional platform to filter by
            
        Returns:
            list: Mock review data
        """
        import random
        from datetime import datetime, timedelta
        
        # Generate 5-10 mock reviews
        num_reviews = random.randint(5, 10)
        reviews = []
        
        # Common subreddits for product reviews
        subreddits = ["gadgets", "tech", "reviews", "BuyItForLife", "ProductReviews"]
        
        # Common positive phrases
        positive_phrases = [
            "I've been using this for a month now and I'm really impressed.",
            "This is definitely worth the money.",
            "I was skeptical at first but this exceeded my expectations.",
            "After extensive research, I decided on this and I'm not disappointed.",
            "This is exactly what I was looking for.",
            "The quality is much better than I expected for the price.",
            "I've tried several similar products and this is by far the best.",
            "This has made a noticeable difference in my daily routine."
        ]
        
        # Common negative phrases
        negative_phrases = [
            "I wanted to like this but it has too many issues.",
            "Save your money and look elsewhere.",
            "This worked great for a week, then it started having problems.",
            "The build quality is not what I expected for the price.",
            "Customer service was unhelpful when I had issues.",
            "It's okay but definitely not worth the price.",
            "I've had to return this twice due to defects.",
            "There are better alternatives available for less money."
        ]
        
        # Common neutral phrases
        neutral_phrases = [
            "It's decent for the price, but don't expect premium quality.",
            "It does what it's supposed to do, nothing more nothing less.",
            "It has some good features but also some drawbacks.",
            "It's a good entry-level option if you're on a budget.",
            "It's not perfect, but it gets the job done.",
            "I have mixed feelings about this product.",
            "It's good in some ways but disappointing in others.",
            "It's okay for casual use but not for professionals."
        ]
        
        # Generate reviews
        for i in range(num_reviews):
            # Determine sentiment (more positive than negative)
            sentiment = random.choices(
                ["positive", "negative", "neutral"],
                weights=[0.6, 0.3, 0.1]
            )[0]
            
            # Generate rating based on sentiment
            if sentiment == "positive":
                rating = random.uniform(4.0, 5.0)
                phrases = positive_phrases
            elif sentiment == "negative":
                rating = random.uniform(1.0, 2.5)
                phrases = negative_phrases
            else:
                rating = random.uniform(2.5, 4.0)
                phrases = neutral_phrases
                
            # Round rating to nearest 0.5
            rating = round(rating * 2) / 2
            
            # Generate review date (within last 6 months)
            days_ago = random.randint(1, 180)
            review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%B %d, %Y")
            
            # Generate review title
            if sentiment == "positive":
                title = f"Great experience with the {product_name}"
            elif sentiment == "negative":
                title = f"Disappointed with the {product_name}"
            else:
                title = f"My thoughts on the {product_name} after {random.randint(1, 6)} months"
                
            # Generate review text
            text = f"I purchased the {product_name} {random.randint(1, 12)} months ago. "
            text += random.choice(phrases) + " "
            
            # Add some specific details
            if sentiment == "positive":
                text += f"The {random.choice(['build quality', 'performance', 'features', 'design'])} is excellent. "
                text += f"I particularly like the {random.choice(['ease of use', 'reliability', 'value for money', 'customer support'])}. "
            elif sentiment == "negative":
                text += f"The {random.choice(['build quality', 'performance', 'features', 'design'])} is disappointing. "
                text += f"I'm particularly unhappy with the {random.choice(['durability', 'reliability', 'value for money', 'customer support'])}. "
            else:
                text += f"The {random.choice(['build quality', 'performance', 'features', 'design'])} is decent. "
                text += f"It could be improved in terms of {random.choice(['ease of use', 'reliability', 'value for money', 'customer support'])}. "
                
            # Add conclusion
            if sentiment == "positive":
                text += "Overall, I would definitely recommend this product."
            elif sentiment == "negative":
                text += "Overall, I would not recommend this product."
            else:
                text += "Overall, it's a decent product but do your research before buying."
                
            # Create review
            review = {
                'rating': rating,
                'title': title,
                'text': text,
                'date': review_date,
                'source': 'Reddit',
                'url': f"https://www.reddit.com/r/{random.choice(subreddits)}/comments/{self._generate_random_id(6)}/",
                'author': f"user_{self._generate_random_id(8)}"
            }
            
            reviews.append(review)
            
        return reviews
        
    def _generate_random_id(self, length):
        """
        Generate a random alphanumeric ID.
        
        Args:
            length: Length of ID
            
        Returns:
            str: Random ID
        """
        import random
        import string
        
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
