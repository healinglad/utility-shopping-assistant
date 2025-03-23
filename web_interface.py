#!/usr/bin/env python3
"""
Web interface for the Shopping Assistant.

This script provides a simple web interface for the Shopping Assistant using Flask.
"""

import sys
import os
import json
from flask import Flask, render_template, request, jsonify

# Add the parent directory to sys.path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopping_assistant.main import ShoppingAssistant
from shopping_assistant.utils.logger import logger
from shopping_assistant.utils.exceptions import ShoppingAssistantError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shopping-assistant-secret-key'

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

# Create static directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)

# Create shopping assistant instance
shopping_assistant = ShoppingAssistant()

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

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
            return jsonify({'error': 'Product is required'}), 400
            
        try:
            budget = float(budget)
        except ValueError:
            return jsonify({'error': 'Budget must be a number'}), 400
            
        # Process preferences
        if preferences:
            preferences = [p.strip() for p in preferences.split(',')]
        else:
            preferences = None
            
        # Search for products
        result = shopping_assistant.search(product, budget, preferences)
        
        # Return result
        return jsonify({'result': result})
        
    except ShoppingAssistantError as e:
        logger.error(f"Shopping Assistant error: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

# Create templates and static files
def create_templates():
    """Create HTML templates."""
    # Create index.html
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shopping Assistant</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Shopping Assistant</h1>
            <p>Find the best products based on your requirements</p>
            
            <div class="search-form">
                <form id="search-form">
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
            
            <div class="loading" id="loading">
                <p>Searching for products...</p>
                <div class="spinner"></div>
            </div>
            
            <div class="results" id="results">
                <h2>Results</h2>
                <pre id="results-content"></pre>
            </div>
            
            <div class="error" id="error">
                <h2>Error</h2>
                <p id="error-message"></p>
            </div>
        </div>
        
        <script src="{{ url_for('static', filename='script.js') }}"></script>
    </body>
    </html>
    """
    
    # Write index.html
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'w') as f:
        f.write(index_html)
        
    # Create style.css
    style_css = """
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
    
    .loading {
        display: none;
        text-align: center;
        margin: 20px 0;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 2s linear infinite;
        margin: 10px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .results, .error {
        display: none;
        margin-top: 20px;
    }
    
    .results h2, .error h2 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .error p {
        color: #e74c3c;
        text-align: left;
    }
    
    pre {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 4px;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    """
    
    # Write style.css
    with open(os.path.join(os.path.dirname(__file__), 'static', 'style.css'), 'w') as f:
        f.write(style_css)
        
    # Create script.js
    script_js = """
    document.addEventListener('DOMContentLoaded', function() {
        const searchForm = document.getElementById('search-form');
        const loadingElement = document.getElementById('loading');
        const resultsElement = document.getElementById('results');
        const resultsContentElement = document.getElementById('results-content');
        const errorElement = document.getElementById('error');
        const errorMessageElement = document.getElementById('error-message');
        
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Hide results and error
            resultsElement.style.display = 'none';
            errorElement.style.display = 'none';
            
            // Show loading
            loadingElement.style.display = 'block';
            
            // Get form data
            const formData = new FormData(searchForm);
            
            // Send request
            fetch('/search', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                loadingElement.style.display = 'none';
                
                if (data.error) {
                    // Show error
                    errorMessageElement.textContent = data.error;
                    errorElement.style.display = 'block';
                } else {
                    // Show results
                    resultsContentElement.textContent = data.result;
                    resultsElement.style.display = 'block';
                }
            })
            .catch(error => {
                // Hide loading
                loadingElement.style.display = 'none';
                
                // Show error
                errorMessageElement.textContent = 'An error occurred: ' + error.message;
                errorElement.style.display = 'block';
            });
        });
    });
    """
    
    # Write script.js
    with open(os.path.join(os.path.dirname(__file__), 'static', 'script.js'), 'w') as f:
        f.write(script_js)

def main():
    """Run the Flask application."""
    # Create templates and static files before starting the app
    create_templates()
    
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
