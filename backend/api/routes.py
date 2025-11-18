"""
API Routes for SQLtoRA Flask application.
Provides REST endpoints for SQL processing pipeline.
"""

from flask import Blueprint, request, jsonify
from backend.tokenizer.tokenizer import Tokenizer
from backend.parser.parser import Parser
from ..ast.builder import ASTBuilder
from backend.semantic.analyzer import SemanticAnalyzer
from backend.ra_converter.converter import RAConverter
from backend.core.exceptions import *
from backend.core.utils import setup_logger

# Create blueprint
api_bp = Blueprint('api', __name__)
logger = setup_logger(__name__)


@api_bp.route('/process', methods=['POST'])
def process_query():
    """
    Process SQL query through complete pipeline.
    
    Expected JSON body:
    {
        "query": "SELECT * FROM employees WHERE salary > 50000"
    }
    
    Returns JSON with all pipeline stages.
    """
    try:
        # Get query from request
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query in request body'
            }), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({
                'error': 'Query cannot be empty'
            }), 400
        
        logger.info(f"Processing query: {query}")
        
        result = {
            'query': query,
            'stages': {}
        }
        
        # Stage 1: Tokenization
        try:
            tokenizer = Tokenizer(query)
            tokens = tokenizer.tokenize()
            result['stages']['tokenization'] = {
                'success': True,
                'tokens': [token.to_dict() for token in tokens]
            }
            logger.info(f"Tokenization successful: {len(tokens)} tokens")
        except TokenizerException as e:
            result['stages']['tokenization'] = {
                'success': False,
                'error': str(e)
            }
            return jsonify(result), 200
        
        # Stage 2: Parsing
        try:
            parser = Parser(tokens)
            parse_tree = parser.parse()
            result['stages']['parsing'] = {
                'success': True,
                'tree': parse_tree.to_dict()
            }
            logger.info("Parsing successful")
        except ParserException as e:
            result['stages']['parsing'] = {
                'success': False,
                'error': str(e)
            }
            return jsonify(result), 200
        
        # Stage 3: AST Building
        try:
            ast_builder = ASTBuilder()
            ast = ast_builder.build(parse_tree)
            result['stages']['ast'] = {
                'success': True,
                'tree': ast.to_dict()
            }
            logger.info("AST building successful")
        except ASTException as e:
            result['stages']['ast'] = {
                'success': False,
                'error': str(e)
            }
            return jsonify(result), 200
        
        # Stage 4: Semantic Analysis
        try:
            semantic_analyzer = SemanticAnalyzer()
            semantic_result = semantic_analyzer.analyze(ast)
            result['stages']['semantic'] = {
                'success': True,
                'analysis': semantic_result
            }
            logger.info(f"Semantic analysis complete: {'valid' if semantic_result['valid'] else 'invalid'}")
        except SemanticException as e:
            result['stages']['semantic'] = {
                'success': False,
                'error': str(e)
            }
            return jsonify(result), 200
        
        # Stage 5: Relational Algebra Conversion
        try:
            ra_converter = RAConverter()
            ra_result = ra_converter.convert(ast)
            result['stages']['relational_algebra'] = {
                'success': True,
                'expression': ra_result['expression'],
                'tree': ra_result['tree'],
                'description': ra_result['description']
            }
            logger.info("RA conversion successful")
        except RAConversionException as e:
            result['stages']['relational_algebra'] = {
                'success': False,
                'error': str(e)
            }
            return jsonify(result), 200
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@api_bp.route('/schema', methods=['GET'])
def get_schema():
    """
    Get available database schema.
    
    Returns the sample schema used for validation.
    """
    from config import Config
    
    return jsonify({
        'schema': Config.SAMPLE_SCHEMA
    }), 200


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'SQLtoRA'
    }), 200