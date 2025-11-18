"""
Configuration module for SQLtoRA application.
Contains all application settings and constants.
"""

class Config:
    """Application configuration class."""
    
    # Flask settings
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    # CORS settings
    CORS_ORIGINS = '*'
    
    # Sample database schema for validation
    SAMPLE_SCHEMA = {
        'employees': ['id', 'name', 'department_id', 'salary', 'hire_date'],
        'departments': ['id', 'name', 'location'],
        'projects': ['id', 'name', 'budget', 'department_id'],
        'students': ['id', 'name', 'age', 'major'],
        'courses': ['id', 'title', 'credits', 'instructor']
    }
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'