#!/usr/bin/env python3
"""
Simple web interface for the Shopping Assistant.

This script provides a basic web interface for the Shopping Assistant without requiring
all the dependencies. It uses Flask to create a simple web server that accepts user inputs
and displays the results.
"""

import sys
import os
import json
from flask import Flask, render_template_string, request

# Add the parent directory to sys.path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shopping-assistant-secret-key'

# HTML template for the index page
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Assistant</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        p {
            text-align: center;
            margin-bottom: 20px;
            color: #7f8c8d;
        }
        
        .search-form {
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input[type="text"],
        input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        small {
            display: block;
            margin-top: 5px;
            color: #7f8c8d;
        }
        
        button {
            display: block;
            width: 100%;
            padding: 10px;
            background-color: #3498db;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background-color: #2980b9;
        }
        
        .results {
            margin-top: 20px;
        }
        
        .results h2 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .error {
            color: #e74c3c;
        }
        
        pre {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .note {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Shopping Assistant</h1>
        <p>Find the best products based on your requirements</p>
        
        <div class="search-form">
            <form method="post" action="/search">
                <div class="form-group">
                    <label for="product">Product:</label>
                    <input type="text" id="product" name="product" placeholder="e.g., laptop, headphones, coffee maker" required>
                </div>
                
                <div class="form-group">
                    <label for="budget">Budget (INR):</label>
                    <input type="number" id="budget" name="budget" placeholder="e.g., 50000" required>
                </div>
                
                <div class="form-group">
                    <label for="preferences">Preferences (optional):</label>
                    <input type="text" id="preferences" name="preferences" placeholder="e.g., gaming, lightweight, wireless">
                    <small>Separate multiple preferences with commas</small>
                </div>
                
                <div class="form-group">
                    <button type="submit">Search</button>
                </div>
            </form>
        </div>
        
        {% if error %}
        <div class="results error">
            <h2>Error</h2>
            <p>{{ error }}</p>
        </div>
        {% endif %}
        
        {% if result %}
        <div class="results">
            <h2>Results</h2>
            <pre>{{ result }}</pre>
        </div>
        {% endif %}
        
        <div class="note">
            <p><strong>Note:</strong> This is a simplified version of the Shopping Assistant web interface. For full functionality, please install all the required dependencies:</p>
            <pre>pip install -r requirements.txt</pre>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the index page."""
    return render_template_string(INDEX_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    try:
        # Get form data
        product = request.form.get('product', '')
        budget = request.form.get('budget', 0)
        preferences = request.form.get('preferences', '')
        
        # Validate input
        if not product:
            return render_template_string(INDEX_TEMPLATE, error="Product is required")
            
        try:
            budget = float(budget)
        except ValueError:
            return render_template_string(INDEX_TEMPLATE, error="Budget must be a number")
            
        # Process preferences
        if preferences:
            preferences = [p.strip() for p in preferences.split(',')]
        else:
            preferences = None
            
        # Try to import the ShoppingAssistant class
        try:
            from shopping_assistant.main import ShoppingAssistant
            
            # Create shopping assistant
            assistant = ShoppingAssistant()
            
            # Search for products
            result = assistant.search(product, budget, preferences)
            
            # Return result
            return render_template_string(INDEX_TEMPLATE, result=result)
            
        except ImportError as e:
            error_message = f"Failed to import required modules: {str(e)}\n\n"
            error_message += "Please install all the required dependencies:\n"
            error_message += "pip install -r requirements.txt"
            return render_template_string(INDEX_TEMPLATE, error=error_message)
            
    except Exception as e:
        return render_template_string(INDEX_TEMPLATE, error=f"An unexpected error occurred: {str(e)}")

def main():
    """Run the Flask application."""
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
