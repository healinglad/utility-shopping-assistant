"""
Custom exceptions for the Shopping Assistant application.
"""

class ShoppingAssistantError(Exception):
    """Base exception for all Shopping Assistant errors."""
    pass

class InputError(ShoppingAssistantError):
    """Exception raised for errors in the input."""
    pass

class ScrapingError(ShoppingAssistantError):
    """Exception raised for errors during web scraping."""
    pass

class NetworkError(ScrapingError):
    """Exception raised for network-related errors."""
    pass

class ParsingError(ScrapingError):
    """Exception raised for errors during HTML parsing."""
    pass

class CacheError(ShoppingAssistantError):
    """Exception raised for errors related to caching."""
    pass

class AnalysisError(ShoppingAssistantError):
    """Exception raised for errors during product analysis."""
    pass

class RecommendationError(ShoppingAssistantError):
    """Exception raised for errors during recommendation generation."""
    pass

class NoResultsError(ShoppingAssistantError):
    """Exception raised when no results are found."""
    pass
