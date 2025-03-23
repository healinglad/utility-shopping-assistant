"""
Web scraper module for the Shopping Assistant application.
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin

# Try to import Selenium-related modules, but provide fallbacks if not available
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Try to import fake_useragent, but provide a fallback if not available
try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False
    # Default user agents to use if fake_useragent is not available
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]

from ..utils.logger import logger
from ..utils.exceptions import ScrapingError, NetworkError, ParsingError
from ..utils.helpers import extract_price, retry_with_backoff

class WebScraper:
    """
    Web scraper for e-commerce platforms.
    """
    
    def __init__(self, config):
        """
        Initialize the WebScraper.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.platforms = config.PLATFORMS
        self.session = None
        self.driver = None
        
        # Initialize user agent
        if FAKE_UA_AVAILABLE:
            self.user_agent = UserAgent()
        else:
            self.user_agent = None
            logger.warning("fake_useragent not available, using default user agents")
        
    def initialize(self):
        """
        Initialize scraping session and webdriver if needed.
        
        Returns:
            self: For method chaining
        """
        # Initialize requests session
        self.session = requests.Session()
        
        # Initialize Selenium webdriver for JavaScript-heavy sites if available
        if SELENIUM_AVAILABLE and self.driver is None:
            try:
                chrome_options = Options()
                if self.config.HEADLESS:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                
                # Install and set up ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(self.config.BROWSER_TIMEOUT)
                logger.info("Selenium webdriver initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Selenium webdriver: {str(e)}")
                self.driver = None
        elif not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available. Some features will be limited.")
            
        logger.info("Web scraper initialized")
        return self
        
    def close(self):
        """
        Close the scraper and release resources.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        if self.session:
            self.session.close()
            self.session = None
            
        logger.info("Web scraper closed")
        
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            self: Initialized scraper
        """
        return self.initialize()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()
        
    def _get_headers(self, platform):
        """
        Get request headers for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            dict: Request headers
        """
        headers = self.platforms[platform]["headers"].copy()
        
        # Use a random user agent
        if FAKE_UA_AVAILABLE and self.user_agent:
            headers["User-Agent"] = self.user_agent.random
        else:
            # Use a random user agent from the default list
            headers["User-Agent"] = random.choice(DEFAULT_USER_AGENTS)
            
        return headers
        
    def _make_request(self, url, platform):
        """
        Make an HTTP request with retry logic.
        
        Args:
            url: URL to request
            platform: Platform name
            
        Returns:
            str: Response text
            
        Raises:
            NetworkError: If request fails
        """
        headers = self._get_headers(platform)
        
        def request_with_retry():
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                raise NetworkError(f"Request failed for {url}: {str(e)}")
                
        # Add a random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, self.config.REQUEST_DELAY))
        
        return retry_with_backoff(
            request_with_retry,
            max_retries=self.config.MAX_RETRIES,
            initial_delay=1,
            backoff_factor=2
        )
        
    def scrape_amazon(self, query):
        """
        Scrape product data from Amazon.
        
        Args:
            query: Search query
            
        Returns:
            list: Product data
        """
        platform = "amazon"
        base_url = self.platforms[platform]["base_url"]
        search_url = self.platforms[platform]["search_url"].format(query=quote_plus(query))
        
        logger.info(f"Scraping Amazon with query: {query}")
        
        try:
            html = self._make_request(search_url, platform)
            soup = BeautifulSoup(html, 'lxml')
            
            products = []
            
            # Find product containers
            product_containers = soup.select('div[data-component-type="s-search-result"]')
            
            for container in product_containers[:self.config.MAX_PRODUCTS_TO_ANALYZE]:
                try:
                    # Extract product data
                    product = self._extract_amazon_product(container, base_url)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting Amazon product: {str(e)}")
                    continue
                    
            logger.info(f"Scraped {len(products)} products from Amazon")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Amazon: {str(e)}")
            raise ScrapingError(f"Failed to scrape Amazon: {str(e)}")
            
    def _extract_amazon_product(self, container, base_url):
        """
        Extract product data from an Amazon product container.
        
        Args:
            container: BeautifulSoup element containing product data
            base_url: Base URL for the platform
            
        Returns:
            dict: Product data or None if extraction fails
        """
        # Skip sponsored products
        if container.select_one('.s-sponsored-label-info-icon'):
            return None
            
        try:
            # Extract product name
            name_element = container.select_one('h2 a span')
            if not name_element:
                return None
            name = name_element.text.strip()
            
            # Extract product URL
            url_element = container.select_one('h2 a')
            url = urljoin(base_url, url_element['href']) if url_element else None
            
            # Extract price
            price_element = container.select_one('.a-price .a-offscreen')
            price_text = price_element.text.strip() if price_element else None
            price = extract_price(price_text)
            
            # Extract rating
            rating_element = container.select_one('i.a-icon-star-small')
            rating = None
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = rating_text.split(' out of ')[0]
                try:
                    rating = float(rating_match)
                except (ValueError, IndexError):
                    rating = None
                    
            # Extract review count
            review_count_element = container.select_one('span.a-size-base.s-underline-text')
            review_count = 0
            if review_count_element:
                try:
                    review_count = int(review_count_element.text.strip().replace(',', ''))
                except ValueError:
                    review_count = 0
                    
            # Extract features/description
            features = []
            feature_elements = container.select('a.a-size-base.a-link-normal.s-underline-text.s-underline-link-text.s-link-style')
            for feature in feature_elements:
                feature_text = feature.text.strip()
                if feature_text and feature_text not in features:
                    features.append(feature_text)
                    
            # Extract image URL
            img_element = container.select_one('img.s-image')
            img_url = img_element['src'] if img_element else None
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'price_text': price_text,
                'rating': rating,
                'review_count': review_count,
                'features': features,
                'image_url': img_url,
                'platform': 'amazon'
            }
            
        except Exception as e:
            logger.warning(f"Error extracting Amazon product data: {str(e)}")
            return None
            
    def scrape_flipkart(self, query):
        """
        Scrape product data from Flipkart.
        
        Args:
            query: Search query
            
        Returns:
            list: Product data
        """
        platform = "flipkart"
        base_url = self.platforms[platform]["base_url"]
        search_url = self.platforms[platform]["search_url"].format(query=quote_plus(query))
        
        logger.info(f"Scraping Flipkart with query: {query}")
        
        try:
            html = self._make_request(search_url, platform)
            soup = BeautifulSoup(html, 'lxml')
            
            products = []
            
            # Find product containers
            product_containers = soup.select('div._1AtVbE')
            
            for container in product_containers[:self.config.MAX_PRODUCTS_TO_ANALYZE]:
                try:
                    # Extract product data
                    product = self._extract_flipkart_product(container, base_url)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Error extracting Flipkart product: {str(e)}")
                    continue
                    
            logger.info(f"Scraped {len(products)} products from Flipkart")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Flipkart: {str(e)}")
            raise ScrapingError(f"Failed to scrape Flipkart: {str(e)}")
            
    def _extract_flipkart_product(self, container, base_url):
        """
        Extract product data from a Flipkart product container.
        
        Args:
            container: BeautifulSoup element containing product data
            base_url: Base URL for the platform
            
        Returns:
            dict: Product data or None if extraction fails
        """
        try:
            # Check if this is a product container
            name_element = container.select_one('div._4rR01T, a.s1Q9rs')
            if not name_element:
                return None
                
            # Extract product name
            name = name_element.text.strip()
            
            # Extract product URL
            url_element = container.select_one('a._1fQZEK, a.s1Q9rs')
            url = urljoin(base_url, url_element['href']) if url_element else None
            
            # Extract price
            price_element = container.select_one('div._30jeq3')
            price_text = price_element.text.strip() if price_element else None
            price = extract_price(price_text)
            
            # Extract rating
            rating_element = container.select_one('div._3LWZlK')
            rating = None
            if rating_element:
                try:
                    rating = float(rating_element.text.strip())
                except ValueError:
                    rating = None
                    
            # Extract review count
            review_count_element = container.select_one('span._2_R_DZ')
            review_count = 0
            if review_count_element:
                review_text = review_count_element.text.strip()
                # Extract numbers from text like "1,234 Reviews & 5,678 Ratings"
                import re
                numbers = re.findall(r'[\d,]+', review_text)
                if numbers:
                    try:
                        review_count = int(numbers[0].replace(',', ''))
                    except (ValueError, IndexError):
                        review_count = 0
                        
            # Extract features/description
            features = []
            feature_elements = container.select('li._21Ahn-')
            for feature in feature_elements:
                feature_text = feature.text.strip()
                if feature_text and feature_text not in features:
                    features.append(feature_text)
                    
            # Extract image URL
            img_element = container.select_one('img._396cs4')
            img_url = img_element['src'] if img_element else None
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'price_text': price_text,
                'rating': rating,
                'review_count': review_count,
                'features': features,
                'image_url': img_url,
                'platform': 'flipkart'
            }
            
        except Exception as e:
            logger.warning(f"Error extracting Flipkart product data: {str(e)}")
            return None
            
    def scrape_reviews(self, product_url, platform):
        """
        Scrape reviews for a specific product.
        
        Args:
            product_url: Product URL
            platform: Platform name
            
        Returns:
            list: Review data
        """
        logger.info(f"Scraping reviews for {platform} product: {product_url}")
        
        if platform == "amazon":
            return self._scrape_amazon_reviews(product_url)
        elif platform == "flipkart":
            return self._scrape_flipkart_reviews(product_url)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
            
    def _scrape_amazon_reviews(self, product_url):
        """
        Scrape reviews from Amazon.
        
        Args:
            product_url: Product URL
            
        Returns:
            list: Review data
        """
        # Extract product ID from URL
        import re
        product_id_match = re.search(r'/dp/([A-Z0-9]+)', product_url)
        if not product_id_match:
            logger.warning(f"Could not extract product ID from URL: {product_url}")
            return []
            
        product_id = product_id_match.group(1)
        reviews_url = f"https://www.amazon.in/product-reviews/{product_id}"
        
        try:
            html = self._make_request(reviews_url, "amazon")
            soup = BeautifulSoup(html, 'lxml')
            
            reviews = []
            review_elements = soup.select('div[data-hook="review"]')
            
            for review_element in review_elements[:10]:  # Limit to 10 reviews
                try:
                    # Extract rating
                    rating_element = review_element.select_one('i[data-hook="review-star-rating"] span')
                    rating = None
                    if rating_element:
                        rating_text = rating_element.text.strip()
                        rating_match = rating_text.split(' out of ')[0]
                        try:
                            rating = float(rating_match)
                        except (ValueError, IndexError):
                            rating = None
                            
                    # Extract title
                    title_element = review_element.select_one('a[data-hook="review-title"] span')
                    title = title_element.text.strip() if title_element else None
                    
                    # Extract text
                    text_element = review_element.select_one('span[data-hook="review-body"] span')
                    text = text_element.text.strip() if text_element else None
                    
                    # Extract date
                    date_element = review_element.select_one('span[data-hook="review-date"]')
                    date = date_element.text.strip() if date_element else None
                    
                    reviews.append({
                        'rating': rating,
                        'title': title,
                        'text': text,
                        'date': date
                    })
                    
                except Exception as e:
                    logger.warning(f"Error extracting Amazon review: {str(e)}")
                    continue
                    
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Amazon reviews: {str(e)}")
            return []
            
    def _scrape_flipkart_reviews(self, product_url):
        """
        Scrape reviews from Flipkart.
        
        Args:
            product_url: Product URL
            
        Returns:
            list: Review data
        """
        reviews_url = f"{product_url}&marketplace=FLIPKART#rating-review"
        
        try:
            html = None
            
            # Use Selenium for Flipkart reviews if available (better results)
            if SELENIUM_AVAILABLE and self.driver:
                try:
                    self.driver.get(reviews_url)
                    
                    # Wait for reviews to load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div._27M-vq'))
                    )
                    
                    # Get page source after JavaScript execution
                    html = self.driver.page_source
                except Exception as e:
                    logger.warning(f"Selenium failed for Flipkart reviews, falling back to requests: {str(e)}")
                    html = None
                    
            # Fall back to regular request if Selenium is not available or failed
            if html is None:
                logger.info("Using regular request for Flipkart reviews")
                html = self._make_request(reviews_url, "flipkart")
                
            soup = BeautifulSoup(html, 'lxml')
            
            reviews = []
            # Try different review container selectors (Flipkart may change them)
            review_elements = soup.select('div._27M-vq, div.t-ZTKy')
            
            for review_element in review_elements[:10]:  # Limit to 10 reviews
                try:
                    # Extract rating
                    rating_element = review_element.select_one('div._3LWZlK')
                    rating = None
                    if rating_element:
                        try:
                            rating = float(rating_element.text.strip())
                        except ValueError:
                            rating = None
                            
                    # Extract title
                    title_element = review_element.select_one('p._2-N8zT')
                    title = title_element.text.strip() if title_element else None
                    
                    # Extract text
                    text_element = review_element.select_one('div.t-ZTKy')
                    text = text_element.text.strip() if text_element else None
                    
                    # If no text found, the review element itself might be the text
                    if not text and hasattr(review_element, 'text'):
                        text = review_element.text.strip()
                    
                    # Extract date
                    date_element = review_element.select_one('p._2sc7ZR')
                    date = date_element.text.strip() if date_element else None
                    
                    # Only add if we have at least some content
                    if rating or title or text:
                        reviews.append({
                            'rating': rating,
                            'title': title,
                            'text': text,
                            'date': date
                        })
                    
                except Exception as e:
                    logger.warning(f"Error extracting Flipkart review: {str(e)}")
                    continue
                    
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping Flipkart reviews: {str(e)}")
            return []
