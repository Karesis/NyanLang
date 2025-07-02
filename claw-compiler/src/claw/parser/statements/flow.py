"""
Defines the parsing function for '@flow' statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ...errors import ParserError
# Re-import the external block parser
from .block import parse_block_statement

def parse_flow_statement(parser: 'Parser') -> ast.FlowStatement:
    """
    Parses a flow definition from the token stream.
    Grammar: '@' IDENTIFIER '{' ... '}'
    """
    at_token = parser.current_token
    assert at_token is not None, "Parser entered invalid state for flow statement"

    if not parser.peek_is(TokenType.IDENTIFIER):
        raise ParserError("Expected an identifier for the flow name after '@'.", at_token)
    
    parser.next_token()
    name_token = parser.current_token
    assert name_token is not None
    name_identifier = ast.Identifier(token=name_token, value=name_token.literal)

    if not parser.peek_is(TokenType.LBRACE):
        raise ParserError(f"Expected '{{' after flow name '{name_identifier.value}'.", name_token)

    parser.next_token() # Consume '{'
    
    # Call the external helper function again.
    body = parse_block_statement(parser)

    return ast.FlowStatement(
        token=at_token,
        name=name_identifier,
        body=body
    )
