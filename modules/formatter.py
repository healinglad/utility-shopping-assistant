"""
Output formatter module for the Shopping Assistant application.
"""

from ..utils.logger import logger
from ..utils.helpers import format_currency

class ResultsFormatter:
    """
    Formats recommendation results for display.
    """
    
    def __init__(self):
        """Initialize the ResultsFormatter."""
        pass
        
    def format_recommendations(self, recommendations):
        """
        Format recommendations according to required output format.
        
        Args:
            recommendations: List of recommendation objects
            
        Returns:
            str: Formatted output
        """
        logger.info("Formatting recommendations")
        
        if not recommendations:
            return "No recommendations found matching your criteria."
            
        formatted_recommendations = []
        
        # Format each recommendation
        for i, recommendation in enumerate(recommendations):
            formatted = self.format_single_recommendation(recommendation, i + 1)
            formatted_recommendations.append(formatted)
            
        # Add summary
        if recommendations:
            top_product = recommendations[0]['product']
            top_name = top_product.get('name', 'the top option')
            
            summary = f"Summary: Based on your requirements, {top_name} appears to be the best match, "
            summary += "offering a good balance of features, price, and reviews."
        else:
            summary = "Summary: No perfect matches found for your criteria."
            
        # Combine all parts
        result = "\n\n".join(formatted_recommendations)
        result += f"\n\n{summary}"
        
        return result
        
    def format_single_recommendation(self, recommendation, index):
        """
        Format a single recommendation.
        
        Args:
            recommendation: Recommendation object
            index: Recommendation index
            
        Returns:
            str: Formatted recommendation
        """
        product = recommendation['product']
        
        # Get product details
        name = product.get('name', 'Unknown Product')
        price = product.get('price', 0)
        price_text = format_currency(price)
        rating = product.get('rating')
        review_count = product.get('review_count', 0)
        platform = product.get('platform', '').capitalize()
        
        # Format key features
        key_features = recommendation.get('key_features', [])
        features_text = ", ".join(key_features) if key_features else "No specific features listed"
        
        # Format review evidence
        if rating and review_count:
            review_evidence = f"{rating} stars from {review_count} reviews on {platform}"
        elif rating:
            review_evidence = f"{rating} stars on {platform}"
        else:
            review_evidence = f"Available on {platform}"
            
        # Format explanation
        explanation = recommendation.get('explanation', '')
        
        # Build formatted output
        formatted = [
            f"Option {index}: {name} - {price_text}",
            f"    Key Features: {features_text}",
            f"    Review Evidence: {review_evidence}",
            f"    Why It Fits: {explanation}"
        ]
        
        # Add forum reviews if available
        if product.get('forum_reviews') and len(product['forum_reviews']) > 0:
            formatted.append(f"    Forum Insights:")
            
            # Get top 2 most relevant forum reviews
            forum_reviews = product['forum_reviews'][:2]
            
            for review in forum_reviews:
                source = review.get('source', 'Forum')
                rating_text = f"{review.get('rating', 'N/A')} stars" if review.get('rating') else ""
                title = review.get('title', '')
                
                # Format the review text (truncate if too long)
                text = review.get('text', '')
                if len(text) > 100:
                    text = text[:100] + "..."
                
                # Add the review
                if rating_text:
                    formatted.append(f"      • {source} ({rating_text}): \"{text}\"")
                else:
                    formatted.append(f"      • {source}: \"{text}\"")
        
        return "\n".join(formatted)
        
    def format_alternatives(self, alternatives, original_budget, original_preferences):
        """
        Format alternative recommendations.
        
        Args:
            alternatives: Alternative recommendations data
            original_budget: Original budget
            original_preferences: Original preferences
            
        Returns:
            str: Formatted alternatives
        """
        logger.info("Formatting alternatives")
        
        formatted = ["No exact matches found for your criteria. Here are some alternatives:"]
        
        # Format increased budget alternatives
        increased_budget = alternatives.get('increased_budget')
        if increased_budget:
            budget = increased_budget.get('budget')
            recommendations = increased_budget.get('recommendations', [])
            
            formatted.append(f"\nWith an increased budget of {format_currency(budget)}:")
            
            for i, recommendation in enumerate(recommendations):
                formatted_rec = self.format_single_recommendation(recommendation, i + 1)
                formatted.append(formatted_rec)
                
        # Format alternative products
        alternative_products = alternatives.get('alternative_products')
        if alternative_products:
            preferences = alternative_products.get('preferences', [])
            recommendations = alternative_products.get('recommendations', [])
            
            pref_text = ", ".join(preferences)
            formatted.append(f"\nWith priority on {pref_text}:")
            
            for i, recommendation in enumerate(recommendations):
                formatted_rec = self.format_single_recommendation(recommendation, i + 1)
                formatted.append(formatted_rec)
                
        # Add suggestions
        suggestions = alternatives.get('suggestions', [])
        if suggestions:
            formatted.append("\nSuggestions:")
            for suggestion in suggestions:
                formatted.append(f"- {suggestion}")
                
        return "\n\n".join(formatted)
        
    def format_error(self, error_message, product, budget, preferences):
        """
        Format error message with suggestions.
        
        Args:
            error_message: Error message
            product: Product search term
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            str: Formatted error message
        """
        logger.info(f"Formatting error: {error_message}")
        
        formatted = [f"Error: {error_message}", ""]
        
        # Add suggestions based on the error
        formatted.append("Suggestions:")
        
        if "No products found" in error_message:
            formatted.append(f"- Try a different search term instead of '{product}'")
            formatted.append("- Check your spelling and try again")
            formatted.append("- Use more general terms (e.g., 'phone' instead of a specific model)")
            
        if "budget" in error_message.lower():
            increased_budget = budget * 1.2
            formatted.append(f"- Consider increasing your budget to {format_currency(increased_budget)}")
            formatted.append("- Look for older models or refurbished items")
            formatted.append("- Wait for sales or special offers")
            
        if preferences:
            formatted.append("- Try reducing the number of preferences to get more results")
            if len(preferences) > 1:
                formatted.append(f"- Focus on your most important preference: {preferences[0]}")
                
        return "\n".join(formatted)
