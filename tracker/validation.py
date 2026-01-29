"""
Input validation functions for the expense tracker.
"""

from datetime import datetime
from tracker.logger import get_logger

logger = get_logger(__name__)


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return False


def validate_amount(amount: float) -> bool:
    """
    Validate that amount is positive.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    if amount <= 0:
        logger.warning(f"Invalid amount (must be > 0): {amount}")
        return False
    return True


def validate_category(category: str) -> bool:
    """
    Validate category is not empty.
    
    Args:
        category: Category to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not category or not category.strip():
        logger.warning("Category cannot be empty")
        return False
    return True


def format_date(date_str: str) -> str:
    """
    Format and validate date string.
    
    Args:
        date_str: Date string (YYYY-MM-DD format or 'today')
        
    Returns:
        Formatted date string
        
    Raises:
        ValueError: If date format is invalid
    """
    if not date_str or date_str.lower() == 'today':
        return datetime.now().strftime("%Y-%m-%d")
    
    if not validate_date(date_str):
        raise ValueError("Error: date must be in YYYY-MM-DD format")
    
    return date_str


def format_amount(amount: float) -> float:
    """
    Format and validate amount.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted amount
        
    Raises:
        ValueError: If amount is invalid
    """
    try:
        amount_float = float(amount)
        if not validate_amount(amount_float):
            raise ValueError("Error: amount must be > 0")
        return round(amount_float, 2)
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError("Error: amount must be a valid number")
        raise


def format_category(category: str) -> str:
    """
    Format and validate category.
    
    Args:
        category: Category to format
        
    Returns:
        Formatted category (lowercase, trimmed)
        
    Raises:
        ValueError: If category is invalid
    """
    if not validate_category(category):
        raise ValueError("Error: category cannot be empty")
    
    return category.strip().lower()