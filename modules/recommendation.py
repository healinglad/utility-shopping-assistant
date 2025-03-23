"""
Recommendation engine module for the Shopping Assistant application.
"""

from ..utils.logger import logger
from ..utils.exceptions import RecommendationError, NoResultsError
from ..utils.helpers import format_currency

class RecommendationEngine:
    """
    Generates product recommendations based on analysis.
    """
    
    def __init__(self, analyzer, config):
        """
        Initialize the RecommendationEngine.
        
        Args:
            analyzer: ProductAnalyzer instance
            config: Configuration settings
        """
        self.analyzer = analyzer
        self.config = config
        self.top_count = config.TOP_RECOMMENDATIONS
        
    def generate_recommendations(self, products, budget, preferences):
        """
        Generate top recommendations.
        
        Args:
            products: List of products
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            list: Top recommendations
            
        Raises:
            NoResultsError: If no suitable products are found
        """
        logger.info("Generating recommendations")
        
        if not products:
            logger.warning("No products to recommend")
            raise NoResultsError("No products found matching your criteria")
            
        # Rank products
        ranked_products = self.analyzer.rank_products(products, budget, preferences)
        
        if not ranked_products:
            logger.warning("No products after ranking")
            raise NoResultsError("No products found within your budget")
            
        # Select top products
        top_products = ranked_products[:self.top_count]
        
        # Enhance recommendations with additional information
        recommendations = []
        
        for product in top_products:
            # Extract key features
            key_features = self.analyzer.extract_key_features(product, preferences)
            
            # Generate explanation
            explanation = self.analyzer.explain_recommendation(product, budget, preferences)
            
            # Create recommendation object
            recommendation = {
                'product': product,
                'key_features': key_features,
                'explanation': explanation
            }
            
            recommendations.append(recommendation)
            
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
        
    def generate_alternatives(self, products, budget, preferences):
        """
        Generate alternative recommendations when no suitable options are found.
        
        Args:
            products: List of products
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            dict: Alternative recommendations and suggestions
        """
        logger.info("Generating alternatives")
        
        alternatives = {
            'increased_budget': None,
            'alternative_products': None,
            'suggestions': []
        }
        
        # Check if we have any products at all
        if not products:
            alternatives['suggestions'].append(
                "No products found. Try a different search term or check your spelling."
            )
            return alternatives
            
        # Try with increased budget
        if budget > 0:
            # Try with 20% higher budget
            increased_budget = budget * 1.2
            
            try:
                # Rank with increased budget
                ranked_products = self.analyzer.rank_products(products, increased_budget, preferences)
                
                if ranked_products:
                    # Select top products
                    top_products = ranked_products[:3]  # Limit to 3 alternatives
                    
                    # Create recommendations
                    recommendations = []
                    for product in top_products:
                        key_features = self.analyzer.extract_key_features(product, preferences)
                        explanation = self.analyzer.explain_recommendation(product, budget, preferences)
                        
                        recommendations.append({
                            'product': product,
                            'key_features': key_features,
                            'explanation': explanation
                        })
                        
                    alternatives['increased_budget'] = {
                        'budget': increased_budget,
                        'recommendations': recommendations
                    }
                    
                    alternatives['suggestions'].append(
                        f"Consider increasing your budget to {format_currency(increased_budget)} to get better options."
                    )
                    
            except Exception as e:
                logger.error(f"Error generating increased budget alternatives: {str(e)}")
                
        # Try with fewer preferences
        if preferences and len(preferences) > 1:
            # Try with the most important preference only
            reduced_preferences = [preferences[0]]
            
            try:
                # Rank with reduced preferences
                ranked_products = self.analyzer.rank_products(products, budget, reduced_preferences)
                
                if ranked_products:
                    # Select top products
                    top_products = ranked_products[:3]  # Limit to 3 alternatives
                    
                    # Create recommendations
                    recommendations = []
                    for product in top_products:
                        key_features = self.analyzer.extract_key_features(product, reduced_preferences)
                        explanation = self.analyzer.explain_recommendation(product, budget, reduced_preferences)
                        
                        recommendations.append({
                            'product': product,
                            'key_features': key_features,
                            'explanation': explanation
                        })
                        
                    alternatives['alternative_products'] = {
                        'preferences': reduced_preferences,
                        'recommendations': recommendations
                    }
                    
                    alternatives['suggestions'].append(
                        f"Consider prioritizing only your most important preference: {reduced_preferences[0]}."
                    )
                    
            except Exception as e:
                logger.error(f"Error generating reduced preference alternatives: {str(e)}")
                
        # Add general suggestions
        if not alternatives['increased_budget'] and not alternatives['alternative_products']:
            alternatives['suggestions'].append(
                "Try searching for a different product category or model."
            )
            alternatives['suggestions'].append(
                "Consider waiting for sales or discounts if your budget is fixed."
            )
            
        logger.info("Generated alternatives and suggestions")
        return alternatives
        
    def format_recommendation(self, recommendation, index):
        """
        Format a recommendation for display.
        
        Args:
            recommendation: Recommendation data
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
        url = product.get('url', '')
        
        # Format rating and review count
        if rating and review_count:
            review_evidence = f"{rating} stars from {review_count} reviews on {platform}"
        elif rating:
            review_evidence = f"{rating} stars on {platform}"
        else:
            review_evidence = f"Available on {platform}"
            
        # Format key features
        key_features = recommendation.get('key_features', [])
        features_text = ", ".join(key_features) if key_features else "No specific features listed"
        
        # Format explanation
        explanation = recommendation.get('explanation', '')
        
        # Build formatted output
        output = [
            f"Option {index + 1}: {name} - {price_text}",
            f"    Key Features: {features_text}",
            f"    Review Evidence: {review_evidence}",
            f"    Why It Fits: {explanation}",
            f"    Link: {url}"
        ]
        
        return "\n".join(output)
        
    def format_recommendations(self, recommendations):
        """
        Format all recommendations for display.
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            str: Formatted recommendations
        """
        if not recommendations:
            return "No recommendations found."
            
        formatted = []
        
        # Format each recommendation
        for i, recommendation in enumerate(recommendations):
            formatted.append(self.format_recommendation(recommendation, i))
            
        # Add summary
        if len(recommendations) > 0:
            top_product = recommendations[0]['product']
            top_name = top_product.get('name', 'the top option')
            
            summary = f"\nSummary: Based on your requirements, {top_name} appears to be the best match, "
            summary += "offering a good balance of features, price, and reviews."
        else:
            summary = "\nSummary: No perfect matches found for your criteria."
            
        formatted.append(summary)
        
        return "\n\n".join(formatted)
        
    def format_alternatives(self, alternatives):
        """
        Format alternative recommendations for display.
        
        Args:
            alternatives: Alternative recommendations data
            
        Returns:
            str: Formatted alternatives
        """
        formatted = ["No exact matches found for your criteria. Here are some alternatives:"]
        
        # Format increased budget alternatives
        increased_budget = alternatives.get('increased_budget')
        if increased_budget:
            budget = increased_budget.get('budget')
            recommendations = increased_budget.get('recommendations', [])
            
            formatted.append(f"\nWith an increased budget of {format_currency(budget)}:")
            
            for i, recommendation in enumerate(recommendations):
                formatted.append(self.format_recommendation(recommendation, i))
                
        # Format alternative products
        alternative_products = alternatives.get('alternative_products')
        if alternative_products:
            preferences = alternative_products.get('preferences', [])
            recommendations = alternative_products.get('recommendations', [])
            
            pref_text = ", ".join(preferences)
            formatted.append(f"\nWith priority on {pref_text}:")
            
            for i, recommendation in enumerate(recommendations):
                formatted.append(self.format_recommendation(recommendation, i))
                
        # Add suggestions
        suggestions = alternatives.get('suggestions', [])
        if suggestions:
            formatted.append("\nSuggestions:")
            for suggestion in suggestions:
                formatted.append(f"- {suggestion}")
                
        return "\n\n".join(formatted)
