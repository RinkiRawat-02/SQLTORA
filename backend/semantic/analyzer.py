"""
Semantic Analyzer - Validates AST semantics.
Checks table and column existence, type compatibility, etc.
"""

from backend.ast.nodes import *
from backend.config import Config
from backend.core.exceptions import SemanticException


class SemanticAnalyzer:
    """
    Performs semantic analysis on AST.
    Validates table and column references against a schema.
    """
    
    def __init__(self, schema=None):
        """
        Initialize semantic analyzer.
        
        Args:
            schema: Database schema dictionary (table_name -> [column_names])
        """
        self.schema = schema or Config.SAMPLE_SCHEMA
        self.errors = []
        self.warnings = []
        self.table_aliases = {}
    
    def analyze(self, ast_node):
        """
        Perform semantic analysis on AST.
        
        Args:
            ast_node: Root AST node (typically SelectNode)
            
        Returns:
            Dictionary with analysis results
        """
        self.errors = []
        self.warnings = []
        self.table_aliases = {}
        
        try:
            if isinstance(ast_node, SelectNode):
                self.analyze_select(ast_node)
        except SemanticException as e:
            self.errors.append(str(e))
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'schema_used': list(self.schema.keys())
        }
    
    def analyze_select(self, node: SelectNode):
        """Analyze SELECT statement."""
        # First, process tables to build alias map
        for table in node.tables:
            self.analyze_table(table)
        
        # Process joins
        for join in node.joins:
            self.analyze_join(join)
        
        # Validate columns
        for column in node.columns:
            self.analyze_column(column)
        
        # Validate WHERE clause
        if node.where:
            self.analyze_condition(node.where)
    
    def analyze_table(self, table: TableNode):
        """Validate table reference."""
        if table.name not in self.schema:
            self.errors.append(f"Table '{table.name}' does not exist in schema")
        else:
            # Register alias
            if table.alias:
                self.table_aliases[table.alias] = table.name
    
    def analyze_join(self, join: JoinNode):
        """Analyze JOIN clause."""
        self.analyze_table(join.table)
        if join.condition:
            self.analyze_condition(join.condition)
    
    def analyze_column(self, column: ColumnNode):
        """Validate column reference."""
        if column.name == '*':
            return  # SELECT * is always valid
        
        # If table is specified
        if column.table:
            # Resolve alias if present
            actual_table = self.table_aliases.get(column.table, column.table)
            
            if actual_table not in self.schema:
                self.errors.append(f"Table '{column.table}' not found")
                return
            
            if column.name not in self.schema[actual_table]:
                self.errors.append(
                    f"Column '{column.name}' does not exist in table '{actual_table}'"
                )
        else:
            # Column without table qualifier - search all tables
            found = False
            found_in_tables = []
            
            for table_name in self.schema:
                if column.name in self.schema[table_name]:
                    found = True
                    found_in_tables.append(table_name)
            
            if not found:
                self.errors.append(f"Column '{column.name}' not found in any table")
            elif len(found_in_tables) > 1:
                self.warnings.append(
                    f"Column '{column.name}' exists in multiple tables: {', '.join(found_in_tables)}. "
                    "Consider using table prefix for clarity."
                )
    
    def analyze_condition(self, condition: ConditionNode):
        """Validate condition in WHERE clause."""
        if isinstance(condition, ComparisonNode):
            self.analyze_expression(condition.left)
            self.analyze_expression(condition.right)
        
        elif isinstance(condition, LogicalNode):
            for operand in condition.operands:
                self.analyze_condition(operand)
    
    def analyze_expression(self, expr: ExpressionNode):
        """Validate expression."""
        if isinstance(expr, IdentifierNode):
            # Check if identifier is a valid column
            if expr.table:
                actual_table = self.table_aliases.get(expr.table, expr.table)
                
                if actual_table not in self.schema:
                    self.errors.append(f"Table '{expr.table}' not found")
                    return
                
                if expr.name not in self.schema[actual_table]:
                    self.errors.append(
                        f"Column '{expr.name}' does not exist in table '{actual_table}'"
                    )
            else:
                # Search all tables
                found = False
                for table_name in self.schema:
                    if expr.name in self.schema[table_name]:
                        found = True
                        break
                
                if not found:
                    self.errors.append(f"Column '{expr.name}' not found in any table")
        
        elif isinstance(expr, ArithmeticNode):
            self.analyze_expression(expr.left)
            self.analyze_expression(expr.right)
        
        # LiteralNode doesn't need validation