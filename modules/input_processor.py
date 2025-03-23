"""
Input processor module for the Shopping Assistant application.
"""

import re
from ..utils.logger import logger
from ..utils.exceptions import InputError
from ..utils.helpers import sanitize_query

class InputProcessor:
    """
    Processes and validates user inputs for the shopping assistant.
    """
    
    def __init__(self):
        """Initialize the InputProcessor."""
        self.product = None
        self.budget = None
        self.preferences = []
        
    def process_input(self, product, budget, preferences=None):
        """
        Process and validate user inputs.
        
        Args:
            product (str): The product to search for
            budget (str or float): The budget in INR
            preferences (list or str, optional): Additional preferences
            
        Returns:
            dict: Processed inputs
            
        Raises:
            InputError: If inputs are invalid
        """
        # Process product
        self._validate_product(product)
        self.product = sanitize_query(product)
        
        # Process budget
        self._validate_budget(budget)
        
        # Process preferences
        self._process_preferences(preferences)
        
        logger.info(f"Processed input: product='{self.product}', budget={self.budget}, "
                   f"preferences={self.preferences}")
        
        return {
            'product': self.product,
            'budget': self.budget,
            'preferences': self.preferences
        }
        
    def _validate_product(self, product):
        """
        Validate the product input.
        
        Args:
            product: The product to validate
            
        Raises:
            InputError: If product is invalid
        """
        if not product:
            raise InputError("Product cannot be empty")
            
        if not isinstance(product, str):
            raise InputError("Product must be a string")
            
        if len(product.strip()) < 2:
            raise InputError("Product must be at least 2 characters long")
            
    def _validate_budget(self, budget):
        """
        Validate and convert the budget input.
        
        Args:
            budget: The budget to validate
            
        Raises:
            InputError: If budget is invalid
        """
        if not budget:
            raise InputError("Budget cannot be empty")
            
        # Convert string to float if necessary
        if isinstance(budget, str):
            # Remove currency symbols and commas
            budget_str = re.sub(r'[^\d.]', '', budget)
            try:
                budget = float(budget_str)
            except ValueError:
                raise InputError(f"Invalid budget format: {budget}")
                
        # Validate budget value
        if not isinstance(budget, (int, float)):
            raise InputError("Budget must be a number")
            
        if budget <= 0:
            raise InputError("Budget must be greater than zero")
            
        self.budget = float(budget)
        
    def _process_preferences(self, preferences):
        """
        Process and validate preferences.
        
        Args:
            preferences: Preferences as string or list
            
        Returns:
            list: Processed preferences
        """
        self.preferences = []
        
        if not preferences:
            return
            
        # Convert string to list if necessary
        if isinstance(preferences, str):
            # Split by commas or spaces
            pref_list = re.split(r'[,\s]+', preferences.strip())
            # Filter out empty strings
            pref_list = [p.strip() for p in pref_list if p.strip()]
        elif isinstance(preferences, list):
            pref_list = preferences
        else:
            raise InputError("Preferences must be a string or list")
            
        # Sanitize each preference
        self.preferences = [sanitize_query(pref) for pref in pref_list]
        
    def generate_search_queries(self):
        """
        Generate optimized search queries for different platforms.
        
        Returns:
            dict: Platform-specific search queries
        """
        if not self.product:
            raise InputError("Product not set. Call process_input first.")
            
        # Base query with product
        base_query = self.product
        
        # Add budget to query if available
        budget_query = f"{base_query} under {int(self.budget)}"
        
        # Add preferences to query
        pref_query = base_query
        if self.preferences:
            pref_str = " ".join(self.preferences)
            pref_query = f"{base_query} {pref_str}"
            
        # Combined query with budget and preferences
        combined_query = budget_query
        if self.preferences:
            pref_str = " ".join(self.preferences)
            combined_query = f"{budget_query} {pref_str}"
            
        return {
            "amazon": {
                "base": base_query,
                "budget": budget_query,
                "preferences": pref_query,
                "combined": combined_query
            },
            "flipkart": {
                "base": base_query,
                "budget": budget_query,
                "preferences": pref_query,
                "combined": combined_query
            }
        }
