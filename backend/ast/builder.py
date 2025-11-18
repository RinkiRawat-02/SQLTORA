"""
AST Builder - Converts parse tree to abstract syntax tree.
"""

from backend.ast.nodes import *
from backend.parser.grammar import ParseTreeNode
from backend.core.exceptions import ASTException


class ASTBuilder:
    """
    Builds an Abstract Syntax Tree from a parse tree.
    """
    
    def build(self, parse_tree: ParseTreeNode):
        """
        Build AST from parse tree.
        
        Args:
            parse_tree: Root of parse tree
            
        Returns:
            Root ASTNode (typically SelectNode)
        """
        if parse_tree.node_type == 'QUERY':
            # Query has one child: the SELECT statement
            return self.build_select(parse_tree.children[0])
        
        raise ASTException(f"Unknown root node type: {parse_tree.node_type}")
    
    def build_select(self, node: ParseTreeNode):
        """Build SelectNode from parse tree."""
        columns = []
        tables = []
        where = None
        joins = []
        distinct = False
        
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            if child.node_type == 'KEYWORD':
                if child.value.upper() == 'DISTINCT':
                    distinct = True
            
            elif child.node_type == 'SELECT_LIST':
                columns = self.build_select_list(child)
            
            elif child.node_type == 'FROM_CLAUSE':
                tables = self.build_from_clause(child)
            
            elif child.node_type == 'WHERE_CLAUSE':
                where = self.build_where_clause(child)
            
            elif child.node_type == 'JOIN_CLAUSE':
                joins.append(self.build_join_clause(child))
            
            i += 1
        
        return SelectNode(columns, tables, where, joins, distinct)
    
    def build_select_list(self, node: ParseTreeNode):
        """Build list of columns from SELECT_LIST node."""
        columns = []
        
        for child in node.children:
            if child.node_type == 'STAR':
                # SELECT * - return special marker
                return [ColumnNode('*')]
            elif child.node_type == 'COLUMN':
                columns.append(self.build_column(child))
        
        return columns
    
    def build_column(self, node: ParseTreeNode):
        """Build ColumnNode from COLUMN parse tree node."""
        name = None
        table = None
        alias = None
        
        for child in node.children:
            if child.node_type == 'TABLE_REF':
                # table.column syntax
                table = child.children[0].value
            elif child.node_type == 'IDENTIFIER':
                if name is None:
                    name = child.value
                else:
                    # This is the column name when table.column syntax is used
                    name = child.value
            elif child.node_type == 'ALIAS':
                alias = child.children[0].value
        
        return ColumnNode(name, table, alias)
    
    def build_from_clause(self, node: ParseTreeNode):
        """Build list of tables from FROM_CLAUSE node."""
        tables = []
        
        for child in node.children:
            if child.node_type == 'TABLE_LIST':
                tables = self.build_table_list(child)
        
        return tables
    
    def build_table_list(self, node: ParseTreeNode):
        """Build list of TableNode from TABLE_LIST."""
        tables = []
        
        for child in node.children:
            if child.node_type == 'TABLE':
                tables.append(self.build_table(child))
        
        return tables
    
    def build_table(self, node: ParseTreeNode):
        """Build TableNode from TABLE parse tree node."""
        name = None
        alias = None
        
        for child in node.children:
            if child.node_type == 'IDENTIFIER':
                name = child.value
            elif child.node_type == 'ALIAS':
                alias = child.children[0].value
        
        return TableNode(name, alias)
    
    def build_where_clause(self, node: ParseTreeNode):
        """Build condition from WHERE_CLAUSE node."""
        for child in node.children:
            if child.node_type != 'KEYWORD':
                return self.build_condition(child)
        return None
    
    def build_join_clause(self, node: ParseTreeNode):
        """Build JoinNode from JOIN_CLAUSE."""
        join_type = 'INNER'  # Default
        table = None
        condition = None
        
        for child in node.children:
            if child.node_type == 'JOIN_TYPE':
                join_type = self.extract_join_type(child)
            elif child.node_type == 'TABLE':
                table = self.build_table(child)
            elif child.node_type == 'ON_CONDITION':
                condition = self.build_condition(child.children[0])
        
        return JoinNode(join_type, table, condition)
    
    def extract_join_type(self, node: ParseTreeNode):
        """Extract join type string from JOIN_TYPE node."""
        parts = []
        for child in node.children:
            if child.node_type == 'KEYWORD':
                parts.append(child.value.upper())
        return ' '.join(parts) if parts else 'INNER'
    
    def build_condition(self, node: ParseTreeNode):
        """Build condition nodes (comparison, logical operations)."""
        if node.node_type == 'AND_CONDITION':
            operands = [self.build_condition(child) for child in node.children]
            return LogicalNode('AND', operands)
        
        elif node.node_type == 'OR_CONDITION':
            operands = [self.build_condition(child) for child in node.children]
            return LogicalNode('OR', operands)
        
        elif node.node_type == 'NOT_CONDITION':
            operand = self.build_condition(node.children[0])
            return LogicalNode('NOT', [operand])
        
        elif node.node_type == 'COMPARISON':
            left = None
            operator = None
            right = None
            
            for child in node.children:
                if child.node_type == 'OPERATOR':
                    operator = child.value
                elif left is None:
                    left = self.build_expression(child)
                else:
                    right = self.build_expression(child)
            
            return ComparisonNode(left, operator, right)
        
        raise ASTException(f"Unknown condition node type: {node.node_type}")
    
    def build_expression(self, node: ParseTreeNode):
        """Build expression nodes."""
        if node.node_type == 'IDENTIFIER':
            return IdentifierNode(node.value)
        
        elif node.node_type == 'COLUMN_REF':
            table = None
            column = None
            for child in node.children:
                if child.node_type == 'TABLE':
                    table = child.value
                elif child.node_type == 'COLUMN':
                    column = child.value
            return IdentifierNode(column, table)
        
        elif node.node_type == 'NUMBER':
            return LiteralNode(node.value, 'NUMBER')
        
        elif node.node_type == 'STRING':
            return LiteralNode(node.value, 'STRING')
        
        elif node.node_type == 'ARITHMETIC':
            left = None
            operator = None
            right = None
            
            for child in node.children:
                if child.node_type == 'OPERATOR':
                    operator = child.value
                elif left is None:
                    left = self.build_expression(child)
                else:
                    right = self.build_expression(child)
            
            return ArithmeticNode(left, operator, right)
        
        raise ASTException(f"Unknown expression node type: {node.node_type}")