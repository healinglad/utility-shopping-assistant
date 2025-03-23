#!/usr/bin/env python3
"""
Shopping Assistant - A utility to help users find the best products to buy based on their inputs.

Usage:
    python main.py --product "laptop" --budget 50000 --preferences "gaming lightweight"
    
Or import and use programmatically:
    from shopping_assistant.main import ShoppingAssistant
    assistant = ShoppingAssistant()
    result = assistant.search("laptop", 50000, ["gaming", "lightweight"])
    print(result)
"""

import sys
import argparse
import importlib.util
import os
from datetime import datetime

# Add the parent directory to sys.path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from shopping_assistant.modules.input_processor import InputProcessor
from shopping_assistant.modules.web_scraper import WebScraper
from shopping_assistant.modules.data_collector import DataCollector
from shopping_assistant.modules.product_analyzer import ProductAnalyzer
from shopping_assistant.modules.recommendation import RecommendationEngine
from shopping_assistant.modules.formatter import ResultsFormatter
import shopping_assistant.config as config
from shopping_assistant.utils.logger import logger
from shopping_assistant.utils.exceptions import (
    ShoppingAssistantError, InputError, ScrapingError, 
    NoResultsError, RecommendationError
)

class ShoppingAssistant:
    """
    Main class for the Shopping Assistant application.
    """
    
    def __init__(self):
        """Initialize the ShoppingAssistant."""
        logger.info("Initializing Shopping Assistant")
        
        # Initialize components
        self.input_processor = InputProcessor()
        self.web_scraper = WebScraper(config)
        self.data_collector = DataCollector(self.web_scraper, config)
        self.product_analyzer = ProductAnalyzer(config)
        self.recommendation_engine = RecommendationEngine(self.product_analyzer, config)
        self.formatter = ResultsFormatter()
        
    def search(self, product, budget, preferences=None):
        """
        Search for products based on input criteria.
        
        Args:
            product (str): The product to search for
            budget (float or str): The budget in INR
            preferences (list or str, optional): Additional preferences
            
        Returns:
            str: Formatted recommendations
            
        Raises:
            ShoppingAssistantError: If an error occurs during the search
        """
        try:
            logger.info(f"Starting search for {product} with budget {budget}")
            
            # Process input
            processed_input = self.input_processor.process_input(product, budget, preferences)
            
            # Generate search queries
            queries = self.input_processor.generate_search_queries()
            
            # Initialize web scraper
            self.web_scraper.initialize()
            
            try:
                # Collect data
                data = self.data_collector.collect_data(queries)
                products = data.get('products', [])
                
                if not products:
                    logger.warning("No products found")
                    alternatives = self.recommendation_engine.generate_alternatives(
                        [], processed_input['budget'], processed_input['preferences']
                    )
                    return self.formatter.format_error(
                        "No products found matching your criteria.",
                        processed_input['product'],
                        processed_input['budget'],
                        processed_input['preferences']
                    )
                
                # Collect reviews for products (including forum reviews)
                logger.info("Collecting reviews for products")
                products_with_reviews = self.data_collector.collect_reviews(products)
                
                # Generate recommendations
                recommendations = self.recommendation_engine.generate_recommendations(
                    products_with_reviews,  # Use products with reviews
                    processed_input['budget'],
                    processed_input['preferences']
                )
                
                # Format recommendations
                result = self.formatter.format_recommendations(recommendations)
                
                logger.info("Search completed successfully")
                return result
                
            except NoResultsError as e:
                logger.warning(f"No results: {str(e)}")
                alternatives = self.recommendation_engine.generate_alternatives(
                    products,
                    processed_input['budget'],
                    processed_input['preferences']
                )
                return self.formatter.format_alternatives(
                    alternatives,
                    processed_input['budget'],
                    processed_input['preferences']
                )
                
            finally:
                # Close web scraper
                self.web_scraper.close()
                
        except InputError as e:
            logger.error(f"Input error: {str(e)}")
            return f"Error: {str(e)}\n\nPlease check your input and try again."
            
        except ScrapingError as e:
            logger.error(f"Scraping error: {str(e)}")
            return f"Error: {str(e)}\n\nThere was a problem accessing product information. Please try again later."
            
        except RecommendationError as e:
            logger.error(f"Recommendation error: {str(e)}")
            return f"Error: {str(e)}\n\nThere was a problem generating recommendations. Please try again."
            
        except ShoppingAssistantError as e:
            logger.error(f"Shopping Assistant error: {str(e)}")
            return f"Error: {str(e)}\n\nAn error occurred. Please try again."
            
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return f"Error: An unexpected error occurred: {str(e)}\n\nPlease try again later."
            
def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Shopping Assistant')
    
    parser.add_argument('--product', required=True, help='The product to search for')
    parser.add_argument('--budget', required=True, type=float, help='Your budget in INR')
    parser.add_argument('--preferences', help='Additional preferences (comma-separated)')
    
    return parser.parse_args()
    
def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Process preferences
    preferences = None
    if args.preferences:
        preferences = [p.strip() for p in args.preferences.split(',')]
        
    # Create shopping assistant
    assistant = ShoppingAssistant()
    
    # Search for products
    result = assistant.search(args.product, args.budget, preferences)
    
    # Print result
    print("\n" + "="*80)
    print(f"SHOPPING ASSISTANT RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(result)
    print("="*80 + "\n")
    
if __name__ == "__main__":
    main()
