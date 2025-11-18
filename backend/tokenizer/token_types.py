"""
Token types and Token class for SQL tokenizer.
"""

from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of all SQL token types."""
    
    # Keywords
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    JOIN = auto()
    INNER = auto()
    LEFT = auto()
    RIGHT = auto()
    FULL = auto()
    OUTER = auto()
    ON = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    AS = auto()
    DISTINCT = auto()
    ORDER = auto()
    BY = auto()
    GROUP = auto()
    HAVING = auto()
    LIMIT = auto()
    UNION = auto()
    INTERSECT = auto()
    EXCEPT = auto()
    
    # Operators
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    
    # Literals and identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    
    # Punctuation
    COMMA = auto()
    DOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    STAR = auto()
    
    # Special
    EOF = auto()
    WHITESPACE = auto()


class Token:
    """Represents a single token in the SQL query."""
    
    def __init__(self, type_: TokenType, value: str, position: int):
        """
        Initialize a token.
        
        Args:
            type_: Token type from TokenType enum
            value: Actual string value of the token
            position: Position in the original query
        """
        self.type = type_
        self.value = value
        self.position = position
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.position})"
    
    def to_dict(self):
        """Convert token to dictionary for JSON serialization."""
        return {
            'type': self.type.name,
            'value': self.value,
            'position': self.position
        }


# Keyword mapping
KEYWORDS = {
    'SELECT': TokenType.SELECT,
    'FROM': TokenType.FROM,
    'WHERE': TokenType.WHERE,
    'JOIN': TokenType.JOIN,
    'INNER': TokenType.INNER,
    'LEFT': TokenType.LEFT,
    'RIGHT': TokenType.RIGHT,
    'FULL': TokenType.FULL,
    'OUTER': TokenType.OUTER,
    'ON': TokenType.ON,
    'AND': TokenType.AND,
    'OR': TokenType.OR,
    'NOT': TokenType.NOT,
    'AS': TokenType.AS,
    'DISTINCT': TokenType.DISTINCT,
    'ORDER': TokenType.ORDER,
    'BY': TokenType.BY,
    'GROUP': TokenType.GROUP,
    'HAVING': TokenType.HAVING,
    'LIMIT': TokenType.LIMIT,
    'UNION': TokenType.UNION,
    'INTERSECT': TokenType.INTERSECT,
    'EXCEPT': TokenType.EXCEPT,
}