"""
Defines the helper function for parsing a block of statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ...errors import ParserError

def parse_block_statement(parser: 'Parser') -> ast.BlockStatement:
    """
    Parses a block of statements enclosed in curly braces '{...}'.
    This function does not handle error recovery; it lets errors propagate
    up to the main `parse_program` loop.
    """
    block_token = parser.current_token
    assert block_token is not None and block_token.token_type == TokenType.LBRACE

    statements: list[ast.Statement] = []
    parser.next_token() # Consume '{'

    while not parser.current_is(TokenType.RBRACE) and not parser.current_is(TokenType.EOF):
        # Call the public statement parser. If it raises an error, let it bubble up.
        stmt = parser.parse_statement()
        if stmt:
            statements.append(stmt)
        
        # The main program loop is responsible for advancing the token.
        # This loop should not advance the token itself, as it would cause
        # tokens to be skipped.
        # Let's re-verify the token advancement logic.
        # `parse_program` loop calls `parse_statement` and then `next_token`.
        # `parse_block_statement` loop calls `parse_statement`.
        # This means inside a block, the token is not advanced. This is a bug.
        # The `parse_block_statement` loop MUST also advance the token.
        parser.next_token()

    if not parser.current_is(TokenType.RBRACE):
        raise ParserError("Expected '}' to close the block.", block_token)

    return ast.BlockStatement(token=block_token, statements=statements)
