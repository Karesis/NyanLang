"""
Defines the parsing function for 'break' statements.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType
from ..precedence import Precedence

def parse_break_statement(parser: 'Parser') -> ast.BreakStatement:
    """
    Parses a break statement from the token stream.
    Grammar: 'break' [Expression]
    """
    break_token = parser.current_token
    assert break_token is not None, "Parser entered invalid state for break statement"

    parser.next_token() # Consume 'break'

    return_value: ast.Expression | None = None
    if parser.current_token and parser.current_token.token_type not in (
        TokenType.RBRACE, TokenType.EOF
    ):
        return_value = parser.parse_expression(Precedence.LOWEST)

    return ast.BreakStatement(token=break_token, return_value=return_value)
