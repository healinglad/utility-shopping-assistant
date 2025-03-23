#!/usr/bin/env python3
"""
Test script for the Shopping Assistant.

This script tests the basic functionality of the Shopping Assistant.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopping_assistant.main import ShoppingAssistant
from shopping_assistant.modules.input_processor import InputProcessor
from shopping_assistant.utils.exceptions import InputError

class TestInputProcessor(unittest.TestCase):
    """Test cases for the InputProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = InputProcessor()
        
    def test_validate_product(self):
        """Test product validation."""
        # Valid product
        self.processor._validate_product("laptop")
        
        # Empty product
        with self.assertRaises(InputError):
            self.processor._validate_product("")
            
        # Too short product
        with self.assertRaises(InputError):
            self.processor._validate_product("a")
            
    def test_validate_budget(self):
        """Test budget validation."""
        # Valid budget as float
        self.processor._validate_budget(1000.0)
        self.assertEqual(self.processor.budget, 1000.0)
        
        # Valid budget as string
        self.processor._validate_budget("2000")
        self.assertEqual(self.processor.budget, 2000.0)
        
        # Valid budget with currency symbol
        self.processor._validate_budget("₹3,000.50")
        self.assertEqual(self.processor.budget, 3000.5)
        
        # Empty budget
        with self.assertRaises(InputError):
            self.processor._validate_budget("")
            
        # Negative budget
        with self.assertRaises(InputError):
            self.processor._validate_budget(-100)
            
        # Invalid budget format
        with self.assertRaises(InputError):
            self.processor._validate_budget("not a number")
            
    def test_process_preferences(self):
        """Test preferences processing."""
        # No preferences
        self.processor._process_preferences(None)
        self.assertEqual(self.processor.preferences, [])
        
        # Empty preferences
        self.processor._process_preferences("")
        self.assertEqual(self.processor.preferences, [])
        
        # Single preference as string
        self.processor._process_preferences("gaming")
        self.assertEqual(self.processor.preferences, ["gaming"])
        
        # Multiple preferences as string
        self.processor._process_preferences("gaming, lightweight")
        self.assertEqual(self.processor.preferences, ["gaming", "lightweight"])
        
        # Preferences as list
        self.processor._process_preferences(["gaming", "lightweight"])
        self.assertEqual(self.processor.preferences, ["gaming", "lightweight"])
        
        # Invalid preferences type
        with self.assertRaises(InputError):
            self.processor._process_preferences(123)
            
    def test_generate_search_queries(self):
        """Test search query generation."""
        # Set up processor
        self.processor.product = "laptop"
        self.processor.budget = 50000
        self.processor.preferences = ["gaming", "lightweight"]
        
        # Generate queries
        queries = self.processor.generate_search_queries()
        
        # Check queries
        self.assertIn("amazon", queries)
        self.assertIn("flipkart", queries)
        self.assertIn("base", queries["amazon"])
        self.assertIn("budget", queries["amazon"])
        self.assertIn("preferences", queries["amazon"])
        self.assertIn("combined", queries["amazon"])
        
        # Check query content
        self.assertEqual(queries["amazon"]["base"], "laptop")
        self.assertEqual(queries["amazon"]["budget"], "laptop under 50000")
        self.assertEqual(queries["amazon"]["preferences"], "laptop gaming lightweight")
        self.assertEqual(queries["amazon"]["combined"], "laptop under 50000 gaming lightweight")

class TestShoppingAssistant(unittest.TestCase):
    """Test cases for the ShoppingAssistant class."""
    
    @patch('shopping_assistant.modules.web_scraper.WebScraper')
    @patch('shopping_assistant.modules.data_collector.DataCollector')
    @patch('shopping_assistant.modules.product_analyzer.ProductAnalyzer')
    @patch('shopping_assistant.modules.recommendation.RecommendationEngine')
    def test_search_input_validation(self, mock_recommendation, mock_analyzer, mock_collector, mock_scraper):
        """Test input validation in search method."""
        # Create shopping assistant with mocked components
        assistant = ShoppingAssistant()
        
        # Empty product
        result = assistant.search("", 1000)
        self.assertIn("Error", result)
        self.assertIn("Product", result)
        
        # Invalid budget
        result = assistant.search("laptop", "not a number")
        self.assertIn("Error", result)
        self.assertIn("Budget", result)
        
        # Negative budget
        result = assistant.search("laptop", -100)
        self.assertIn("Error", result)
        self.assertIn("Budget", result)

def main():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    main()
