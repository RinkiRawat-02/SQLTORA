"""
SQL Parser - Syntax analysis stage.
Builds a parse tree from tokens according to SQL grammar.
"""

from backend.tokenizer.token_types import Token, TokenType
from backend.parser.grammar import ParseTreeNode
from backend.core.exceptions import ParserException


class Parser:
    """
    Recursive descent parser for SQL queries.
    """
    
    def __init__(self, tokens):
        """
        Initialize parser with token list.
        
        Args:
            tokens: List of Token objects from tokenizer
        """
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to the next token."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def peek(self, offset=1):
        """
        Look ahead at future tokens.
        
        Args:
            offset: How many tokens ahead to look
            
        Returns:
            Token at position + offset, or None
        """
        peek_pos = self.position + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType):
        """
        Consume a token of the expected type.
        
        Args:
            token_type: Expected token type
            
        Returns:
            The consumed token
            
        Raises:
            ParserException: If current token doesn't match expected type
        """
        if self.current_token.type != token_type:
            raise ParserException(
                f"Expected {token_type.name} but got {self.current_token.type.name} "
                f"at position {self.current_token.position}"
            )
        token = self.current_token
        self.advance()
        return token
    
    def match(self, *token_types):
        """
        Check if current token matches any of the given types.
        
        Args:
            token_types: Token types to match against
            
        Returns:
            True if current token matches any type
        """
        return self.current_token and self.current_token.type in token_types
    
    def parse(self):
        """
        Parse tokens into a parse tree.
        
        Returns:
            Root ParseTreeNode
            
        Raises:
            ParserException: If parsing fails
        """
        return self.parse_query()
    
    def parse_query(self):
        """Parse a complete SQL query."""
        node = ParseTreeNode('QUERY')
        node.add_child(self.parse_select_statement())
        return node
    
    def parse_select_statement(self):
        """Parse SELECT statement."""
        node = ParseTreeNode('SELECT_STMT')
        
        # SELECT keyword
        select_token = self.expect(TokenType.SELECT)
        node.add_child(ParseTreeNode('KEYWORD', select_token.value))
        
        # Optional DISTINCT
        if self.match(TokenType.DISTINCT):
            distinct_token = self.current_token
            self.advance()
            node.add_child(ParseTreeNode('KEYWORD', distinct_token.value))
        
        # Select list (columns)
        node.add_child(self.parse_select_list())
        
        # FROM clause
        if self.match(TokenType.FROM):
            from_token = self.current_token
            self.advance()
            from_node = ParseTreeNode('FROM_CLAUSE')
            from_node.add_child(ParseTreeNode('KEYWORD', from_token.value))
            from_node.add_child(self.parse_table_list())
            node.add_child(from_node)
        
        # Optional JOIN clauses
        while self.match(TokenType.JOIN, TokenType.INNER, TokenType.LEFT, 
                         TokenType.RIGHT, TokenType.FULL):
            node.add_child(self.parse_join_clause())
        
        # Optional WHERE clause
        if self.match(TokenType.WHERE):
            where_token = self.current_token
            self.advance()
            where_node = ParseTreeNode('WHERE_CLAUSE')
            where_node.add_child(ParseTreeNode('KEYWORD', where_token.value))
            where_node.add_child(self.parse_condition())
            node.add_child(where_node)
        
        return node
    
    def parse_select_list(self):
        """Parse the column list in SELECT clause."""
        node = ParseTreeNode('SELECT_LIST')
        
        # Check for SELECT *
        if self.match(TokenType.STAR):
            star_token = self.current_token
            self.advance()
            node.add_child(ParseTreeNode('STAR', star_token.value))
            return node
        
        # Parse column list
        node.add_child(self.parse_column())
        
        while self.match(TokenType.COMMA):
            self.advance()
            node.add_child(self.parse_column())
        
        return node
    
    def parse_column(self):
        """Parse a single column reference."""
        node = ParseTreeNode('COLUMN')
        
        # First identifier (table name or column name)
        id_token = self.expect(TokenType.IDENTIFIER)
        id_node = ParseTreeNode('IDENTIFIER', id_token.value)
        
        # Check for table.column syntax
        if self.match(TokenType.DOT):
            self.advance()
            table_node = ParseTreeNode('TABLE_REF')
            table_node.add_child(id_node)
            node.add_child(table_node)
            
            col_token = self.expect(TokenType.IDENTIFIER)
            node.add_child(ParseTreeNode('IDENTIFIER', col_token.value))
        else:
            node.add_child(id_node)
        
        # Optional AS alias
        if self.match(TokenType.AS):
            self.advance()
            alias_token = self.expect(TokenType.IDENTIFIER)
            alias_node = ParseTreeNode('ALIAS')
            alias_node.add_child(ParseTreeNode('IDENTIFIER', alias_token.value))
            node.add_child(alias_node)
        
        return node
    
    def parse_table_list(self):
        """Parse table list in FROM clause."""
        node = ParseTreeNode('TABLE_LIST')
        
        node.add_child(self.parse_table())
        
        while self.match(TokenType.COMMA):
            self.advance()
            node.add_child(self.parse_table())
        
        return node
    
    def parse_table(self):
        """Parse a single table reference."""
        node = ParseTreeNode('TABLE')
        
        table_token = self.expect(TokenType.IDENTIFIER)
        node.add_child(ParseTreeNode('IDENTIFIER', table_token.value))
        
        # Optional AS alias
        if self.match(TokenType.AS):
            self.advance()
            alias_token = self.expect(TokenType.IDENTIFIER)
            alias_node = ParseTreeNode('ALIAS')
            alias_node.add_child(ParseTreeNode('IDENTIFIER', alias_token.value))
            node.add_child(alias_node)
        
        return node
    
    def parse_join_clause(self):
        """Parse JOIN clause."""
        node = ParseTreeNode('JOIN_CLAUSE')
        
        # Join type
        join_type_node = ParseTreeNode('JOIN_TYPE')
        if self.match(TokenType.INNER):
            join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
            self.advance()
        elif self.match(TokenType.LEFT):
            join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
            self.advance()
            if self.match(TokenType.OUTER):
                join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
                self.advance()
        elif self.match(TokenType.RIGHT):
            join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
            self.advance()
            if self.match(TokenType.OUTER):
                join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
                self.advance()
        elif self.match(TokenType.FULL):
            join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
            self.advance()
            if self.match(TokenType.OUTER):
                join_type_node.add_child(ParseTreeNode('KEYWORD', self.current_token.value))
                self.advance()
        
        node.add_child(join_type_node)
        
        # JOIN keyword
        self.expect(TokenType.JOIN)
        node.add_child(ParseTreeNode('KEYWORD', 'JOIN'))
        
        # Table name
        node.add_child(self.parse_table())
        
        # ON condition
        if self.match(TokenType.ON):
            self.advance()
            on_node = ParseTreeNode('ON_CONDITION')
            on_node.add_child(self.parse_condition())
            node.add_child(on_node)
        
        return node
    
    def parse_condition(self):
        """Parse WHERE/ON condition."""
        return self.parse_or_condition()
    
    def parse_or_condition(self):
        """Parse OR expression."""
        left = self.parse_and_condition()
        
        while self.match(TokenType.OR):
            self.advance()
            node = ParseTreeNode('OR_CONDITION')
            node.add_child(left)
            node.add_child(self.parse_and_condition())
            left = node
        
        return left
    
    def parse_and_condition(self):
        """Parse AND expression."""
        left = self.parse_not_condition()
        
        while self.match(TokenType.AND):
            self.advance()
            node = ParseTreeNode('AND_CONDITION')
            node.add_child(left)
            node.add_child(self.parse_not_condition())
            left = node
        
        return left
    
    def parse_not_condition(self):
        """Parse NOT expression."""
        if self.match(TokenType.NOT):
            self.advance()
            node = ParseTreeNode('NOT_CONDITION')
            node.add_child(self.parse_primary_condition())
            return node
        
        return self.parse_primary_condition()
    
    def parse_primary_condition(self):
        """Parse primary condition (comparison or parenthesized)."""
        # Parenthesized condition
        if self.match(TokenType.LPAREN):
            self.advance()
            node = self.parse_condition()
            self.expect(TokenType.RPAREN)
            return node
        
        # Comparison
        return self.parse_comparison()
    
    def parse_comparison(self):
        """Parse comparison expression."""
        node = ParseTreeNode('COMPARISON')
        
        # Left side
        node.add_child(self.parse_expression())
        
        # Comparison operator
        if self.match(TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN,
                     TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op_node = ParseTreeNode('OPERATOR', self.current_token.value)
            node.add_child(op_node)
            self.advance()
        else:
            raise ParserException(f"Expected comparison operator at position {self.current_token.position}")
        
        # Right side
        node.add_child(self.parse_expression())
        
        return node
    
    def parse_expression(self):
        """Parse arithmetic expression."""
        left = self.parse_term()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            self.advance()
            node = ParseTreeNode('ARITHMETIC')
            node.add_child(left)
            node.add_child(ParseTreeNode('OPERATOR', op_token.value))
            node.add_child(self.parse_term())
            left = node
        
        return left
    
    def parse_term(self):
        """Parse term (for operator precedence)."""
        left = self.parse_factor()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current_token
            self.advance()
            node = ParseTreeNode('ARITHMETIC')
            node.add_child(left)
            node.add_child(ParseTreeNode('OPERATOR', op_token.value))
            node.add_child(self.parse_factor())
            left = node
        
        return left
    
    def parse_factor(self):
        """Parse factor (identifier, number, string, or parenthesized expression)."""
        # Number
        if self.match(TokenType.NUMBER):
            node = ParseTreeNode('NUMBER', self.current_token.value)
            self.advance()
            return node
        
        # String
        if self.match(TokenType.STRING):
            node = ParseTreeNode('STRING', self.current_token.value)
            self.advance()
            return node
        
        # Identifier (possibly with table prefix)
        if self.match(TokenType.IDENTIFIER):
            id_token = self.current_token
            self.advance()
            
            # Check for table.column
            if self.match(TokenType.DOT):
                self.advance()
                node = ParseTreeNode('COLUMN_REF')
                node.add_child(ParseTreeNode('TABLE', id_token.value))
                col_token = self.expect(TokenType.IDENTIFIER)
                node.add_child(ParseTreeNode('COLUMN', col_token.value))
                return node
            else:
                return ParseTreeNode('IDENTIFIER', id_token.value)
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return node
        
        raise ParserException(f"Unexpected token {self.current_token.type.name} at position {self.current_token.position}")