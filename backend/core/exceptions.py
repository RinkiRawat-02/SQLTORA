"""
Custom exceptions for SQLtoRA compiler pipeline.
"""

class SQLtoRAException(Exception):
    """Base exception for all SQLtoRA errors."""
    pass


class TokenizerException(SQLtoRAException):
    """Raised when tokenization fails."""
    pass


class ParserException(SQLtoRAException):
    """Raised when parsing fails."""
    pass


class ASTException(SQLtoRAException):
    """Raised when AST construction fails."""
    pass


class SemanticException(SQLtoRAException):
    """Raised when semantic analysis fails."""
    pass


class RAConversionException(SQLtoRAException):
    """Raised when relational algebra conversion fails."""
    pass