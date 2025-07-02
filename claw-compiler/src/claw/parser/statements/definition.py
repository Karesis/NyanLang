"""
Defines the parsing function for 'def' (struct definition) statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ...errors import ParserError
from .types import parse_type_annotation

def parse_def_statement(parser: 'Parser') -> ast.DefStatement:
    """
    Parses a struct definition from the token stream.
    Grammar: 'def' '{' FieldList '}' IDENTIFIER
    """
    def_token = parser.current_token
    assert def_token is not None, "Parser entered invalid state for def statement"

    if not parser.expect_peek(TokenType.LBRACE):
        raise ParserError("Expected '{' after 'def' keyword.", def_token)
    
    fields = _parse_field_list(parser)

    # After the field list, we expect the struct's name.
    if not parser.peek_is(TokenType.IDENTIFIER):
        # Fix for Issue #1: Assert that current_token is not None before use.
        # The token at this point would be the closing '}', so it's a safe assertion.
        assert parser.current_token is not None
        raise ParserError("Expected an identifier for the struct name after '}'.", parser.current_token)

    parser.next_token()
    name_token = parser.current_token
    assert name_token is not None
    name_identifier = ast.Identifier(token=name_token, value=name_token.literal)

    return ast.DefStatement(
        token=def_token,
        name=name_identifier,
        fields=fields
    )

def _parse_field_list(parser: 'Parser') -> dict[ast.Identifier, ast.TypeNode]:
    """Helper function to parse the field list of a struct definition."""
    # Fix for Issue #3: The dictionary should be keyed by the field name (str)
    # to correctly check for duplicates.
    fields: dict[str, tuple[ast.Identifier, ast.TypeNode]] = {}
    
    # This will be the final dictionary returned, matching the AST node's type.
    final_fields: dict[ast.Identifier, ast.TypeNode] = {}

    # Check for an empty field list, e.g., `def {} MyEmptyStruct`.
    if parser.peek_is(TokenType.RBRACE):
        parser.next_token() # Consume '}'
        return final_fields

    parser.next_token() # Move to the first field name.

    while not parser.current_is(TokenType.RBRACE) and not parser.current_is(TokenType.EOF):
        # Fix for Issue #2: Assert current_token is not None before use.
        if not parser.current_is(TokenType.IDENTIFIER):
            assert parser.current_token is not None
            raise ParserError("Expected an identifier for field name.", parser.current_token)
        
        field_name_token = parser.current_token
        assert field_name_token is not None
        field_name_ident = ast.Identifier(token=field_name_token, value=field_name_token.literal)

        if not parser.expect_peek(TokenType.COLON):
            raise ParserError(f"Expected ':' after field name '{field_name_ident.value}'.", field_name_token)
        
        parser.next_token()
        field_type = parse_type_annotation(parser)
        
        # Fix for Issue #3: Check for the string value in the keys.
        if field_name_ident.value in fields:
            raise ParserError(f"Duplicate field name '{field_name_ident.value}' in struct definition.", field_name_token)
        
        # Fix for Issue #3: Store by string key initially.
        fields[field_name_ident.value] = (field_name_ident, field_type)

        parser.next_token()

        if parser.current_is(TokenType.COMMA):
            parser.next_token()

    # Fix for Issue #4: Assert current_token is not None before use.
    if not parser.current_is(TokenType.RBRACE):
        assert parser.current_token is not None
        raise ParserError("Expected '}' to close struct definition.", parser.current_token)

    # Convert the temporary dictionary to the final format.
    for _, (ident, type_node) in fields.items():
        final_fields[ident] = type_node

    return final_fields
