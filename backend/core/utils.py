"""
Utility functions and helpers for SQLtoRA.
"""

import logging
from backend.config import Config


def setup_logger(name):
    """
    Setup logger with consistent formatting.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(Config.LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def tree_to_dict(node):
    """
    Convert tree node to dictionary for JSON serialization.
    
    Args:
        node: Tree node object
        
    Returns:
        Dictionary representation
    """
    if node is None:
        return None
    
    result = {
        'type': node.__class__.__name__,
        'value': getattr(node, 'value', None)
    }
    
    # Add children if they exist
    if hasattr(node, 'children') and node.children:
        result['children'] = [tree_to_dict(child) for child in node.children]
    
    # Add specific attributes based on node type
    for attr in ['table', 'columns', 'condition', 'left', 'right', 'operator']:
        if hasattr(node, attr):
            val = getattr(node, attr)
            if isinstance(val, (list, tuple)):
                result[attr] = [tree_to_dict(item) if hasattr(item, '__dict__') else item for item in val]
            elif hasattr(val, '__dict__'):
                result[attr] = tree_to_dict(val)
            else:
                result[attr] = val
    
    return result