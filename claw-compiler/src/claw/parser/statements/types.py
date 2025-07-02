"""
Defines helper functions for parsing type annotations within statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ...errors import ParserError

def parse_type_annotation(parser: 'Parser') -> ast.TypeNode:
    """
    Parses a type annotation.

    This function is called when the parser is positioned at the start of a
    type definition (e.g., after the ':' in a `let` statement). It handles:
    - Simple types: `i32`, `MyStruct`
    - Mutable types: `~i32`
    """
    # We need to check the current token to decide which kind of type it is.
    token = parser.current_token
    assert token is not None, "Parser entered invalid state: expected a type, got None."

    # Handle mutable types, e.g., `~i32`.
    if token.token_type == TokenType.TILDE:
        # The current token is '~'. We need to parse the underlying type.
        parser.next_token() # Consume '~', move to the type name.
        
        # Recursively call this function to parse the base type.
        # This allows for future extensions like `~MyStruct` or even `~~i32` if desired.
        base_type = parse_type_annotation(parser)
        
        return ast.MutableType(token=token, base_type=base_type)

    # Handle simple identifier-based types, e.g., `i32`.
    if token.token_type == TokenType.IDENTIFIER:
        return ast.SimpleType(token=token)

    # If we encounter a token that cannot start a type, it's a syntax error.
    raise ParserError(f"Unexpected token '{token.literal}' found when expecting a type.", token)
