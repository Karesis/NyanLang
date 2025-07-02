"""
Defines the parsing function for 'let' statements (variable declarations).
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from .types import parse_type_annotation
from ..precedence import Precedence # <-- Import Precedence

def parse_let_statement(parser: 'Parser') -> ast.LetStatement:
    """
    Parses a variable declaration statement from the token stream.
    Grammar: IDENTIFIER ':' TypeAnnotation [':=' Expression]
    """
    name_token = parser.current_token
    assert name_token is not None, "Parser entered invalid state for let statement"
    
    name_identifier = ast.Identifier(token=name_token, value=name_token.literal)

    parser.next_token() # Consume ':'

    parser.next_token() # Move to the start of the type annotation.
    
    type_node = parse_type_annotation(parser)
    is_mutable = isinstance(type_node, ast.MutableType)

    # Check for an optional assignment part (':=')
    value_expression: ast.Expression | None = None
    if parser.peek_is(TokenType.COLON_ASSIGN):
        parser.next_token()  # Consume ':='
        parser.next_token()  # Move to the start of the expression
        
        # Correctly use the Precedence enum instead of a raw integer.
        value_expression = parser.parse_expression(Precedence.LOWEST)

    return ast.LetStatement(
        token=name_token,
        name=name_identifier,
        mutable=is_mutable,
        value_type=type_node,
        value=value_expression
    )
