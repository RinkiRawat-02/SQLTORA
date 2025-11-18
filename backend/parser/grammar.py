"""
Grammar rules for SQL parser.
Defines the structure of valid SQL statements.
"""


class ParseTreeNode:
    """
    Node in the parse tree.
    Represents a grammar production or terminal.
    """
    
    def __init__(self, node_type: str, value=None):
        """
        Initialize parse tree node.
        
        Args:
            node_type: Type of node (e.g., 'SELECT_STMT', 'IDENTIFIER')
            value: Value for terminal nodes
        """
        self.node_type = node_type
        self.value = value
        self.children = []
    
    def add_child(self, child):
        """Add a child node."""
        if child:
            self.children.append(child)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = {
            'type': self.node_type,
        }
        
        if self.value is not None:
            result['value'] = self.value
        
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        
        return result
    
    def __repr__(self):
        return f"ParseTreeNode({self.node_type}, {self.value})"


# Grammar rules (BNF-like notation in comments)
"""
SQL Grammar (Simplified):

query ::= select_stmt

select_stmt ::= SELECT [DISTINCT] select_list FROM table_list [where_clause] [join_clause]

select_list ::= STAR | column_list

column_list ::= column [, column]*

column ::= IDENTIFIER [. IDENTIFIER] [AS IDENTIFIER]

table_list ::= table [, table]*

table ::= IDENTIFIER [AS IDENTIFIER]

where_clause ::= WHERE condition

join_clause ::= join_type JOIN IDENTIFIER ON condition

join_type ::= [INNER | LEFT | RIGHT | FULL [OUTER]]

condition ::= expression comparison_op expression
           | condition AND condition
           | condition OR condition
           | NOT condition
           | ( condition )

expression ::= IDENTIFIER [. IDENTIFIER]
            | NUMBER
            | STRING
            | expression math_op expression

comparison_op ::= = | != | <> | < | > | <= | >=

math_op ::= + | - | * | /
"""