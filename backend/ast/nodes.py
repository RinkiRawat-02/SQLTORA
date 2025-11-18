"""
AST Node definitions.
Each node represents a semantic construct in the SQL query.
"""


class ASTNode:
    """Base class for all AST nodes."""
    
    def to_dict(self):
        """Convert node to dictionary for JSON serialization."""
        result = {'type': self.__class__.__name__}
        
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, ASTNode) else item
                    for item in value
                ]
            elif isinstance(value, ASTNode):
                result[key] = value.to_dict()
            else:
                result[key] = value
        
        return result


class SelectNode(ASTNode):
    """Represents a SELECT statement."""
    
    def __init__(self, columns, tables, where=None, joins=None, distinct=False):
        self.columns = columns  # List of ColumnNode
        self.tables = tables    # List of TableNode
        self.where = where      # ConditionNode or None
        self.joins = joins or [] # List of JoinNode
        self.distinct = distinct


class ColumnNode(ASTNode):
    """Represents a column in SELECT clause."""
    
    def __init__(self, name, table=None, alias=None):
        self.name = name
        self.table = table  # Table name or None
        self.alias = alias  # Alias or None


class TableNode(ASTNode):
    """Represents a table reference."""
    
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias


class JoinNode(ASTNode):
    """Represents a JOIN operation."""
    
    def __init__(self, join_type, table, condition):
        self.join_type = join_type  # 'INNER', 'LEFT', 'RIGHT', 'FULL'
        self.table = table          # TableNode
        self.condition = condition  # ConditionNode


class ConditionNode(ASTNode):
    """Base class for conditions."""
    pass


class ComparisonNode(ConditionNode):
    """Represents a comparison operation."""
    
    def __init__(self, left, operator, right):
        self.left = left        # ExpressionNode
        self.operator = operator  # '=', '<', '>', '<=', '>=', '!=', '<>'
        self.right = right      # ExpressionNode


class LogicalNode(ConditionNode):
    """Represents logical operations (AND, OR, NOT)."""
    
    def __init__(self, operator, operands):
        self.operator = operator  # 'AND', 'OR', 'NOT'
        self.operands = operands  # List of ConditionNode


class ExpressionNode(ASTNode):
    """Base class for expressions."""
    pass


class IdentifierNode(ExpressionNode):
    """Represents a column identifier."""
    
    def __init__(self, name, table=None):
        self.name = name
        self.table = table


class LiteralNode(ExpressionNode):
    """Represents a literal value."""
    
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type  # 'NUMBER', 'STRING'


class ArithmeticNode(ExpressionNode):
    """Represents arithmetic operations."""
    
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator  # '+', '-', '*', '/'
        self.right = right