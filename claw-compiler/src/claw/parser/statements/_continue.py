"""
Defines the parsing function for 'continue' (con) statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ..precedence import Precedence

def parse_continue_statement(parser: 'Parser') -> ast.ContinueStatement:
    """
    Parses a continue statement from the token stream.
    Grammar: 'con' [Expression]
    """
    continue_token = parser.current_token
    assert continue_token is not None, "Parser entered invalid state for continue statement"

    parser.next_token() # Consume 'con'

    return_value: ast.Expression | None = None
    if parser.current_token and parser.current_token.token_type not in (
        TokenType.RBRACE, TokenType.EOF
    ):
        return_value = parser.parse_expression(Precedence.LOWEST)

    return ast.ContinueStatement(token=continue_token, return_value=return_value)
