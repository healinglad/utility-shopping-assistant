# Shopping Assistant

A Python utility that helps users find the best products to buy based on their inputs.

## Features

- Search for products across multiple e-commerce platforms (Amazon, Flipkart)
- Filter products based on budget constraints
- Match products to user preferences
- Analyze product ratings and reviews
- Gather insights from forums like Reddit
- Provide detailed recommendations with explanations
- Suggest alternatives when no perfect matches are found

## Requirements

- Python 3.8 or higher
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd shopping-assistant
   ```

2. Install dependencies:

   **Using the installation script (recommended):**
   ```
   python install.py
   ```
   This script will guide you through the installation process and let you choose between a full or minimal installation.

   **Manual installation:**

   For full installation (all features):
   ```
   pip install -r requirements.txt
   ```

   For minimal installation (basic features only):
   ```
   pip install -r requirements_minimal.txt
   ```

3. Set up environment variables (for Reddit forum reviews):

   Copy the example environment file:
   ```
   cp .env.example .env
   ```

   Edit the `.env` file and add your Reddit API credentials:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=python:shopping-assistant:v0.1.0 (by /u/your_username)
   ```

   To get Reddit API credentials:
   - Create a Reddit account if you don't have one
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create app" or "Create another app" at the bottom
   - Fill in the details (name, description, etc.)
   - Select "script" as the app type
   - Set the redirect URI to http://localhost:8000
   - Click "Create app"
   - Your client ID is the string under the app name
   - Your client secret is listed as "secret"

## Usage

### Command Line Interface

```bash
python main.py --product "laptop" --budget 50000 --preferences "gaming,lightweight"
```

Arguments:
- `--product`: The product you want to research and buy (required)
- `--budget`: Your budget in INR (required)
- `--preferences`: Additional preferences as comma-separated values (optional)

### Web Interface

There are two web interface options:

#### Full Web Interface (requires all dependencies)

```bash
python web_interface.py
```

This will start a web server at http://localhost:5000 where you can access a user-friendly interface to search for products.

#### Simple Web Interface (minimal dependencies)

```bash
python simple_web_interface.py
```

This will start a basic web server at http://localhost:5000 with a simplified interface that requires only Flask to be installed.

### Programmatic Usage

```python
from shopping_assistant.main import ShoppingAssistant

# Create shopping assistant
assistant = ShoppingAssistant()

# Search for products
result = assistant.search(
    product="laptop",
    budget=50000,
    preferences=["gaming", "lightweight"]
)

# Print result
print(result)
```

## Example Output

```
Option 1: ASUS TUF Gaming F15 Core i5 10th Gen - (8 GB/512 GB SSD/Windows 11 Home/4 GB Graphics/NVIDIA GeForce GTX 1650/144 Hz) FX506LH-HN258W Gaming Laptop - ₹49,990.00
    Key Features: 15.6 inch, 8 GB RAM, 512 GB SSD, Windows 11, NVIDIA GeForce GTX 1650
    Review Evidence: 4.3 stars from 1,245 reviews on Flipkart
    Why It Fits: Within your budget of ₹50000. Highly rated at 4.3 stars with 1245 reviews. Matches your preferences for gaming and lightweight. Available on Flipkart
    Forum Insights:
      • Reddit (4.5 stars): "I've been using this for a month now and I'm really impressed. The battery life is excellent..."
      • Reddit (3.5 stars): "It's decent for the price, but don't expect premium quality. The build quality is solid..."

Option 2: Lenovo IdeaPad Gaming 3 Ryzen 5 Hexa Core 5600H - (8 GB/512 GB SSD/Windows 11 Home/4 GB Graphics/NVIDIA GeForce GTX 1650/120 Hz) 15ACH6 Gaming Laptop - ₹48,990.00
    Key Features: 15.6 inch, 8 GB RAM, 512 GB SSD, Windows 11, NVIDIA GeForce GTX 1650
    Review Evidence: 4.2 stars from 987 reviews on Flipkart
    Why It Fits: Within your budget of ₹50000. Highly rated at 4.2 stars with 987 reviews. Matches your preferences for gaming. Available on Flipkart
    Forum Insights:
      • Reddit (4.0 stars): "After extensive research, I decided on this and I'm not disappointed. Great value for money."
      • Reddit (3.0 stars): "It has some good features but also some drawbacks. The performance is decent but the fan noise is annoying."

Summary: Based on your requirements, ASUS TUF Gaming F15 appears to be the best match, offering a good balance of features, price, and reviews.
```

## Project Structure

```
shopping_assistant/
├── main.py                 # Entry point for the application
├── example.py              # Example usage
├── requirements.txt        # Python dependencies
├── config.py               # Configuration settings
├── .env.example            # Example environment variables
├── cache/                  # Directory for cached data
├── modules/
│   ├── __init__.py
│   ├── input_processor.py  # Handles user input processing
│   ├── web_scraper.py      # Web scraping functionality
│   ├── data_collector.py   # Data aggregation from multiple sources
│   ├── forum_scraper.py    # Forum scraping for reviews
│   ├── product_analyzer.py # Analysis and ranking of products
│   ├── recommendation.py   # Recommendation engine
│   └── formatter.py        # Output formatting
└── utils/
    ├── __init__.py
    ├── helpers.py          # Helper functions
    ├── exceptions.py       # Custom exceptions
    └── logger.py           # Logging functionality
```

## Forum Reviews Feature

The shopping assistant now includes reviews from forums like Reddit alongside traditional e-commerce reviews. This provides a more comprehensive view of products by incorporating insights from real user discussions.

### How Forum Reviews Work

1. When you search for a product, the assistant collects reviews from both e-commerce platforms and forums.
2. For Reddit, it searches across multiple relevant subreddits like r/gadgets, r/tech, r/reviews, etc.
3. It performs sentiment analysis on the forum posts to estimate ratings.
4. The most relevant forum reviews are displayed in the "Forum Insights" section of each recommendation.

### Configuration

You can customize the forum reviews feature in `config.py`:

- `INCLUDE_FORUM_REVIEWS`: Toggle to enable/disable forum reviews (default: True)
- `MAX_FORUM_REVIEWS`: Maximum number of forum reviews to fetch per product (default: 10)
- `REDDIT_SUBREDDITS`: List of subreddits to search for product reviews
- `FORCE_REAL_REDDIT_DATA`: Force using real Reddit data when credentials are available (default: True)

## Limitations

- Web scraping is dependent on the structure of e-commerce websites, which may change over time
- Results are limited to the products available on the supported platforms
- The accuracy of recommendations depends on the quality of data available on the websites
- Forum reviews require valid Reddit API credentials to fetch real data (falls back to mock data if not available)

## License

[MIT License](LICENSE)
