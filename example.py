#!/usr/bin/env python3
"""
Example usage of the Shopping Assistant.

This script demonstrates how to use the Shopping Assistant programmatically.
"""

import sys
import os

# Add the parent directory to sys.path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopping_assistant.main import ShoppingAssistant

def example_search():
    """
    Example search using the Shopping Assistant.
    """
    print("Shopping Assistant Example")
    print("=========================\n")
    
    # Create shopping assistant
    assistant = ShoppingAssistant()
    
    # Example 1: Search for a laptop with a budget of 50000 INR
    print("Example 1: Search for a laptop with a budget of 50000 INR")
    result = assistant.search("laptop", 50000, ["gaming", "lightweight"])
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Example 2: Search for headphones with a budget of 2000 INR
    print("Example 2: Search for headphones with a budget of 2000 INR")
    result = assistant.search("headphones", 2000, "wireless")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Example 3: Search for a coffee maker with a budget of 5000 INR
    print("Example 3: Search for a coffee maker with a budget of 5000 INR")
    result = assistant.search("coffee maker", 5000, ["automatic", "espresso"])
    print(result)
    
    # Example 4: Search for a smartphone with a budget of 20000 INR with forum reviews
    print("\n" + "="*50 + "\n")
    print("Example 4: Search for a smartphone with a budget of 20000 INR with forum reviews")
    
    # Enable forum reviews and force real Reddit data in config
    import shopping_assistant.config as config
    config.INCLUDE_FORUM_REVIEWS = True
    config.FORCE_REAL_REDDIT_DATA = True
    
    # Print confirmation
    print("\nForum reviews enabled:", config.INCLUDE_FORUM_REVIEWS)
    print("Force real Reddit data:", config.FORCE_REAL_REDDIT_DATA)
    print("Reddit credentials:", "Configured" if config.REDDIT_CLIENT_ID else "Not configured")
    print("\nSearching for smartphone with Reddit reviews...\n")
    
    # Create a new assistant instance to ensure config changes are applied
    new_assistant = ShoppingAssistant()
    
    # Search with explicit logging
    result = new_assistant.search("smartphone", 20000, ["camera", "battery"])
    print(result)
    
if __name__ == "__main__":
    example_search()
