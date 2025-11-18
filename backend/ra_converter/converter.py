"""
Relational Algebra Converter - Converts AST to Relational Algebra.
Uses proper RA symbols: σ (selection), π (projection), × (cartesian product), 
⨝ (join), ρ (rename), ∪ (union), ∩ (intersection), − (difference)
"""

from backend.ast.nodes import *
from backend.core.exceptions import RAConversionException


class RAConverter:
    """
    Converts validated AST to Relational Algebra expressions.
    """
    
    def convert(self, ast_node):
        """
        Convert AST to relational algebra.
        
        Args:
            ast_node: Root AST node (typically SelectNode)
            
        Returns:
            Dictionary with RA expression and tree structure
        """
        if isinstance(ast_node, SelectNode):
            return self.convert_select(ast_node)
        
        raise RAConversionException(f"Unknown AST node type: {type(ast_node)}")
    
    def convert_select(self, node: SelectNode):
        """
        Convert SELECT statement to relational algebra.
        
        Strategy:
        1. Start with base tables (possibly with renames for aliases)
        2. Apply cartesian product or joins
        3. Apply selection (WHERE clause)
        4. Apply projection (SELECT columns)
        5. Apply DISTINCT if needed
        """
        # Build the RA expression bottom-up
        
        # Step 1: Base relations with aliases
        base_expr = self.build_base_relations(node.tables)
        
        # Step 2: Apply joins
        if node.joins:
            base_expr = self.apply_joins(base_expr, node.joins)
        elif len(node.tables) > 1:
            # Multiple tables without explicit join = cartesian product
            base_expr = self.apply_cartesian_product(node.tables)
        
        # Step 3: Apply selection (WHERE clause)
        if node.where:
            selection_expr = self.convert_condition(node.where)
            base_expr = f"σ_{{{selection_expr}}}({base_expr})"
        
        # Step 4: Apply projection (SELECT columns)
        projection_list = self.build_projection_list(node.columns)
        base_expr = f"π_{{{projection_list}}}({base_expr})"
        
        # Step 5: Apply DISTINCT if needed
        if node.distinct:
            base_expr = f"δ({base_expr})"  # δ represents duplicate elimination
        
        # Build tree structure for visualization
        tree = self.build_ra_tree(node)
        
        return {
            'expression': base_expr,
            'tree': tree,
            'description': self.generate_description(node)
        }
    
    def build_base_relations(self, tables):
        """Build base relation expression with aliases."""
        if not tables:
            raise RAConversionException("No tables specified")
        
        if len(tables) == 1:
            table = tables[0]
            if table.alias:
                return f"ρ_{{{table.alias}}}({table.name})"
            return table.name
        
        # Multiple tables - will be joined or cartesian product
        result = []
        for table in tables:
            if table.alias:
                result.append(f"ρ_{{{table.alias}}}({table.name})")
            else:
                result.append(table.name)
        
        return ' × '.join(result)
    
    def apply_cartesian_product(self, tables):
        """Apply cartesian product for multiple tables."""
        result = []
        for table in tables:
            if table.alias:
                result.append(f"ρ_{{{table.alias}}}({table.name})")
            else:
                result.append(table.name)
        return ' × '.join(result)
    
    def apply_joins(self, base_expr, joins):
        """Apply JOIN operations."""
        result = base_expr
        
        for join in joins:
            condition = self.convert_condition(join.condition)
            table_expr = join.table.name
            
            if join.table.alias:
                table_expr = f"ρ_{{{join.table.alias}}}({table_expr})"
            
            # Use appropriate join symbol based on type
            if 'LEFT' in join.join_type:
                join_symbol = '⟕'
            elif 'RIGHT' in join.join_type:
                join_symbol = '⟖'
            elif 'FULL' in join.join_type:
                join_symbol = '⟗'
            else:  # INNER or default
                join_symbol = '⨝'
            
            result = f"({result} {join_symbol}_{{{condition}}} {table_expr})"
        
        return result
    
    def build_projection_list(self, columns):
        """Build projection attribute list."""
        if len(columns) == 1 and columns[0].name == '*':
            return '*'
        
        result = []
        for col in columns:
            if col.table:
                result.append(f"{col.table}.{col.name}")
            else:
                result.append(col.name)
            
            if col.alias:
                result[-1] += f" AS {col.alias}"
        
        return ', '.join(result)
    
    def convert_condition(self, condition: ConditionNode):
        """Convert condition to RA predicate."""
        if isinstance(condition, ComparisonNode):
            left = self.convert_expression(condition.left)
            right = self.convert_expression(condition.right)
            return f"{left} {condition.operator} {right}"
        
        elif isinstance(condition, LogicalNode):
            if condition.operator == 'AND':
                operands = [self.convert_condition(op) for op in condition.operands]
                return ' ∧ '.join(operands)
            elif condition.operator == 'OR':
                operands = [self.convert_condition(op) for op in condition.operands]
                return ' ∨ '.join(operands)
            elif condition.operator == 'NOT':
                operand = self.convert_condition(condition.operands[0])
                return f"¬({operand})"
        
        return "unknown_condition"
    
    def convert_expression(self, expr: ExpressionNode):
        """Convert expression to RA format."""
        if isinstance(expr, IdentifierNode):
            if expr.table:
                return f"{expr.table}.{expr.name}"
            return expr.name
        
        elif isinstance(expr, LiteralNode):
            if expr.literal_type == 'STRING':
                return f"'{expr.value}'"
            return expr.value
        
        elif isinstance(expr, ArithmeticNode):
            left = self.convert_expression(expr.left)
            right = self.convert_expression(expr.right)
            return f"({left} {expr.operator} {right})"
        
        return "unknown"
    
    def build_ra_tree(self, node: SelectNode):
        """Build tree structure for RA operations."""
        operations = []
        
        # Base tables
        for table in node.tables:
            operations.append({
                'operation': 'Relation',
                'symbol': table.name,
                'details': f"Alias: {table.alias}" if table.alias else "No alias"
            })
        
        # Joins or Cartesian Product
        if node.joins:
            for join in node.joins:
                operations.append({
                    'operation': f'{join.join_type} Join',
                    'symbol': '⨝',
                    'details': f"On: {self.convert_condition(join.condition)}"
                })
        elif len(node.tables) > 1:
            operations.append({
                'operation': 'Cartesian Product',
                'symbol': '×',
                'details': f"{len(node.tables)} tables"
            })
        
        # Selection (WHERE)
        if node.where:
            operations.append({
                'operation': 'Selection',
                'symbol': 'σ',
                'details': self.convert_condition(node.where)
            })
        
        # Projection (SELECT)
        operations.append({
            'operation': 'Projection',
            'symbol': 'π',
            'details': self.build_projection_list(node.columns)
        })
        
        # DISTINCT
        if node.distinct:
            operations.append({
                'operation': 'Duplicate Elimination',
                'symbol': 'δ',
                'details': 'Remove duplicates'
            })
        
        return operations
    
    def generate_description(self, node: SelectNode):
        """Generate human-readable description of RA expression."""
        parts = []
        
        # Tables
        table_names = [t.name for t in node.tables]
        parts.append(f"From table(s): {', '.join(table_names)}")
        
        # Joins
        if node.joins:
            join_info = [f"{j.join_type} join with {j.table.name}" for j in node.joins]
            parts.append(f"Joins: {', '.join(join_info)}")
        
        # WHERE
        if node.where:
            parts.append(f"Filter by: {self.convert_condition(node.where)}")
        
        # SELECT
        col_list = self.build_projection_list(node.columns)
        parts.append(f"Project columns: {col_list}")
        
        # DISTINCT
        if node.distinct:
            parts.append("Remove duplicates")
        
        return ' → '.join(parts)