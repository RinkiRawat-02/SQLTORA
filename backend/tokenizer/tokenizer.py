"""
SQL Tokenizer - Lexical analysis stage.
Converts SQL query string into a stream of tokens.
"""

from backend.tokenizer.token_types import Token, TokenType, KEYWORDS
from backend.core.exceptions import TokenizerException


class Tokenizer:
    """
    Tokenizes SQL queries into a list of tokens.
    """
    
    def __init__(self, query: str):
        """
        Initialize tokenizer with SQL query.
        
        Args:
            query: SQL query string to tokenize
        """
        self.query = query
        self.position = 0
        self.current_char = self.query[0] if query else None
    
    def advance(self):
        """Move to the next character in the query."""
        self.position += 1
        if self.position >= len(self.query):
            self.current_char = None
        else:
            self.current_char = self.query[self.position]
    
    def peek(self, offset=1):
        """
        Look ahead at the next character without advancing.
        
        Args:
            offset: How many characters ahead to look
            
        Returns:
            Character at position + offset, or None
        """
        peek_pos = self.position + offset
        if peek_pos >= len(self.query):
            return None
        return self.query[peek_pos]
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """
        Read a numeric literal.
        
        Returns:
            Number string (can include decimal point)
        """
        start_pos = self.position
        num_str = ''
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        
        return Token(TokenType.NUMBER, num_str, start_pos)
    
    def read_string(self):
        """
        Read a string literal (single or double quoted).
        
        Returns:
            String token
        """
        start_pos = self.position
        quote_char = self.current_char
        self.advance()  # Skip opening quote
        
        string_val = ''
        while self.current_char and self.current_char != quote_char:
            string_val += self.current_char
            self.advance()
        
        if self.current_char != quote_char:
            raise TokenizerException(f"Unterminated string at position {start_pos}")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, string_val, start_pos)
    
    def read_identifier(self):
        """
        Read an identifier or keyword.
        
        Returns:
            Token (either IDENTIFIER or specific keyword type)
        """
        start_pos = self.position
        identifier = ''
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            identifier += self.current_char
            self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(identifier.upper(), TokenType.IDENTIFIER)
        return Token(token_type, identifier, start_pos)
    
    def tokenize(self):
        """
        Tokenize the entire SQL query.
        
        Returns:
            List of Token objects
            
        Raises:
            TokenizerException: If tokenization fails
        """
        tokens = []
        
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Numbers
            if self.current_char.isdigit():
                tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char in ('"', "'"):
                tokens.append(self.read_string())
                continue
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.read_identifier())
                continue
            
            # Operators and punctuation
            start_pos = self.position
            
            if self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', start_pos))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TokenType.DOT, '.', start_pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', start_pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', start_pos))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TokenType.SEMICOLON, ';', start_pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.STAR, '*', start_pos))
                self.advance()
            elif self.current_char == '+':
                tokens.append(Token(TokenType.PLUS, '+', start_pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, '-', start_pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIVIDE, '/', start_pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TokenType.EQUALS, '=', start_pos))
                self.advance()
            elif self.current_char == '<':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_pos))
                    self.advance()
                    self.advance()
                elif self.peek() == '>':
                    tokens.append(Token(TokenType.NOT_EQUALS, '<>', start_pos))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LESS_THAN, '<', start_pos))
                    self.advance()
            elif self.current_char == '>':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_pos))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GREATER_THAN, '>', start_pos))
                    self.advance()
            elif self.current_char == '!':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.NOT_EQUALS, '!=', start_pos))
                    self.advance()
                    self.advance()
                else:
                    raise TokenizerException(f"Unexpected character '!' at position {start_pos}")
            else:
                raise TokenizerException(f"Unexpected character '{self.current_char}' at position {start_pos}")
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', self.position))
        return tokens