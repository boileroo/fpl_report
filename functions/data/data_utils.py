from typing import Any, List, Optional, Union

def safe_get_nested_value(data: dict, keys: List[str], default: Optional[Any] = None) -> Any:
    """
    Safely get a nested value from a dictionary using a list of keys.
    
    Args:
        data (dict): The dictionary to search in
        keys (list): List of keys to traverse
        default: Default value to return if key path doesn't exist
        
    Returns:
        The value at the nested key path or default value
    """
    current = data
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default

def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: Union[int, float] = 0) -> float:
    """
    Safely divide two numbers, returning a default value if denominator is zero.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value to return if denominator is zero
        
    Returns:
        The result of division or default value
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ValueError):
        return default

def format_currency(value: Union[int, float]) -> str:
    """
    Format a numeric value as currency.
    
    Args:
        value: The numeric value to format
        
    Returns:
        Formatted currency string
    """
    try:
        return f"£{value:,.2f}"
    except (TypeError, ValueError):
        return "£0.00"

def format_percentage(value: Union[int, float]) -> str:
    """
    Format a numeric value as percentage.
    
    Args:
        value: The numeric value to format
        
    Returns:
        Formatted percentage string
    """
    try:
        return f"{value:.1f}%"
    except (TypeError, ValueError):
        return "0.0%"

def clamp_value(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value between minimum and maximum values.
    
    Args:
        value: The value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    try:
        return max(min_val, min(value, max_val))
    except (TypeError, ValueError):
        return min_val