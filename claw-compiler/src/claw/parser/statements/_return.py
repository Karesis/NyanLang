"""
Defines the parsing function for 'return' statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ..precedence import Precedence

def parse_return_statement(parser: 'Parser') -> ast.ReturnStatement:
    """
    Parses a return statement from the token stream.
    Grammar: 'ret' [Expression]
    """
    # The current token when this function is called is 'ret'.
    ret_token = parser.current_token
    assert ret_token is not None, "Parser entered invalid state for return statement"

    parser.next_token() # Consume the 'ret' token.

    return_value: ast.Expression | None = None

    # Check if there is an expression to parse. A simple heuristic is to check
    # that the current token is not something that would typically end a block
    # or the file itself.
    if parser.current_token and parser.current_token.token_type not in (
        TokenType.RBRACE, # '}'
        TokenType.EOF,
    ):
         return_value = parser.parse_expression(Precedence.LOWEST)

    return ast.ReturnStatement(token=ret_token, return_value=return_value)
