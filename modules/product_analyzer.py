"""
Product analyzer module for the Shopping Assistant application.
"""

import re
from collections import Counter

from ..utils.logger import logger
from ..utils.exceptions import AnalysisError

class ProductAnalyzer:
    """
    Analyzes and ranks products based on various criteria.
    """
    
    def __init__(self, config):
        """
        Initialize the ProductAnalyzer.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        self.budget_flexibility = config.BUDGET_FLEXIBILITY
        self.min_reviews = config.MIN_REVIEWS
        
    def filter_by_budget(self, products, budget):
        """
        Filter products by budget constraint.
        
        Args:
            products: List of products
            budget: Budget constraint
            
        Returns:
            list: Filtered products
        """
        logger.info(f"Filtering products by budget: {budget}")
        
        # Calculate maximum price with flexibility
        max_price = budget * (1 + self.budget_flexibility)
        
        # Filter products
        filtered_products = []
        over_budget_products = []
        
        for product in products:
            price = product.get('price')
            
            if price is None:
                continue
                
            if price <= budget:
                filtered_products.append(product)
            elif price <= max_price:
                # Mark as over budget but within flexibility
                product['over_budget'] = True
                over_budget_products.append(product)
                
        # If we have very few products within budget, include some over budget
        if len(filtered_products) < 3 and over_budget_products:
            # Sort over budget products by price
            over_budget_products.sort(key=lambda p: p.get('price', float('inf')))
            # Add enough to have at least 3 products (if available)
            filtered_products.extend(over_budget_products[:3 - len(filtered_products)])
            
        logger.info(f"Filtered to {len(filtered_products)} products within budget")
        return filtered_products
        
    def score_by_preferences(self, products, preferences):
        """
        Score products based on preference matching.
        
        Args:
            products: List of products
            preferences: List of preferences
            
        Returns:
            list: Products with preference scores
        """
        if not preferences:
            logger.info("No preferences provided, skipping preference scoring")
            for product in products:
                product['preference_score'] = 0
                product['matched_preferences'] = []
            return products
            
        logger.info(f"Scoring products by preferences: {preferences}")
        
        scored_products = []
        
        for product in products:
            # Initialize preference score and matched preferences
            preference_score = 0
            matched_preferences = []
            
            # Get product name and features
            name = product.get('name', '').lower()
            features = [f.lower() for f in product.get('features', [])]
            
            # Combine name and features for matching
            product_text = name + ' ' + ' '.join(features)
            
            # Check each preference
            for preference in preferences:
                pref_lower = preference.lower()
                
                # Check for exact match
                if pref_lower in product_text:
                    preference_score += 1
                    matched_preferences.append(preference)
                    continue
                    
                # Check for partial match (words within preference)
                pref_words = pref_lower.split()
                if len(pref_words) > 1:
                    matches = sum(1 for word in pref_words if word in product_text)
                    if matches / len(pref_words) >= 0.5:  # At least half of the words match
                        preference_score += 0.5
                        matched_preferences.append(preference)
                        
            # Add scores to product
            product['preference_score'] = preference_score
            product['matched_preferences'] = matched_preferences
            
            scored_products.append(product)
            
        logger.info("Completed preference scoring")
        return scored_products
        
    def calculate_review_score(self, product):
        """
        Calculate a score based on ratings and review count.
        
        Args:
            product: Product data
            
        Returns:
            float: Review score
        """
        rating = product.get('rating')
        review_count = product.get('review_count', 0)
        
        if rating is None or review_count < self.min_reviews:
            return 0
            
        # Base score is the rating (0-5)
        base_score = rating
        
        # Bonus for having many reviews (logarithmic scale)
        import math
        if review_count > 0:
            review_bonus = min(1, math.log10(review_count) / 3)  # Max bonus of 1 point
        else:
            review_bonus = 0
            
        return base_score + review_bonus
        
    def rank_products(self, products, budget, preferences):
        """
        Rank products by combined score.
        
        Args:
            products: List of products
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            list: Ranked products
        """
        logger.info("Ranking products")
        
        # Filter by budget
        filtered_products = self.filter_by_budget(products, budget)
        
        # Score by preferences
        scored_products = self.score_by_preferences(filtered_products, preferences)
        
        # Calculate combined score
        for product in scored_products:
            # Get individual scores
            preference_score = product.get('preference_score', 0)
            review_score = self.calculate_review_score(product)
            
            # Price score (higher for lower prices relative to budget)
            price = product.get('price', budget)
            if price <= 0:
                price_score = 0
            else:
                price_ratio = price / budget
                if price_ratio <= 1:
                    # Price is within budget
                    price_score = 1 - (price_ratio * 0.5)  # 0.5 to 1.0 for within budget
                else:
                    # Price is over budget
                    price_score = 0.5 - ((price_ratio - 1) * 2)  # 0.5 to 0 for over budget
                    price_score = max(0, price_score)  # Ensure non-negative
                    
            # Calculate combined score
            # Weights: 40% preference, 40% reviews, 20% price
            combined_score = (
                (preference_score * 2) +  # Preference score (0-2 typically)
                (review_score * 0.8) +    # Review score (0-6 typically)
                (price_score * 2)         # Price score (0-2)
            )
            
            product['combined_score'] = combined_score
            product['review_score'] = review_score
            product['price_score'] = price_score
            
        # Sort by combined score (descending)
        ranked_products = sorted(
            scored_products,
            key=lambda p: p.get('combined_score', 0),
            reverse=True
        )
        
        logger.info("Products ranked successfully")
        return ranked_products
        
    def extract_key_features(self, product, preferences):
        """
        Extract key features from product data.
        
        Args:
            product: Product data
            preferences: User preferences
            
        Returns:
            list: Key features
        """
        # Start with explicit features
        features = product.get('features', [])
        
        # Extract features from product name
        name = product.get('name', '')
        
        # Look for technical specifications in the name
        specs = re.findall(r'\b\d+(?:\.\d+)?(?:GB|TB|MP|GHz|inch|cm|mm|mAh)\b', name)
        features.extend(specs)
        
        # Look for features in parentheses
        parentheses_features = re.findall(r'\(([^)]+)\)', name)
        for pf in parentheses_features:
            features.extend([f.strip() for f in pf.split(',')])
            
        # Add matched preferences
        matched_prefs = product.get('matched_preferences', [])
        features.extend(matched_prefs)
        
        # Remove duplicates while preserving order
        unique_features = []
        for feature in features:
            if feature and feature not in unique_features:
                unique_features.append(feature)
                
        # Prioritize features that match preferences
        if preferences:
            def preference_match_score(feature):
                score = 0
                feature_lower = feature.lower()
                for pref in preferences:
                    pref_lower = pref.lower()
                    if pref_lower == feature_lower:
                        score += 2  # Exact match
                    elif pref_lower in feature_lower or feature_lower in pref_lower:
                        score += 1  # Partial match
                return score
                
            # Sort features by preference match score
            unique_features.sort(key=preference_match_score, reverse=True)
            
        # Limit to top features
        return unique_features[:5]
        
    def explain_recommendation(self, product, budget, preferences):
        """
        Generate explanation for recommendation.
        
        Args:
            product: Product data
            budget: Budget constraint
            preferences: List of preferences
            
        Returns:
            str: Explanation
        """
        explanation = []
        
        # Price consideration
        price = product.get('price', 0)
        if price <= budget:
            explanation.append(f"Within your budget of ₹{budget}")
        else:
            over_by = price - budget
            over_percent = (over_by / budget) * 100
            explanation.append(f"Slightly over budget by ₹{over_by:.2f} ({over_percent:.1f}%)")
            
        # Rating and reviews
        rating = product.get('rating')
        review_count = product.get('review_count', 0)
        if rating and review_count >= self.min_reviews:
            explanation.append(f"Highly rated at {rating} stars with {review_count} reviews")
            
        # Preference matches
        matched_prefs = product.get('matched_preferences', [])
        if matched_prefs:
            if len(matched_prefs) == 1:
                explanation.append(f"Matches your preference for {matched_prefs[0]}")
            else:
                pref_text = ", ".join(matched_prefs[:-1]) + " and " + matched_prefs[-1]
                explanation.append(f"Matches your preferences for {pref_text}")
                
        # Platform consideration
        platform = product.get('platform', '').capitalize()
        if platform:
            explanation.append(f"Available on {platform}")
            
        return ". ".join(explanation)
