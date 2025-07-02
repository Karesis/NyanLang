"""
Defines the parselet for handling grouped expressions, e.g., `(a + b)`.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token, TokenType
from ...errors import ParserError
from ..interfaces import PrefixParselet
from ..precedence import Precedence

class GroupedExpressionParselet(PrefixParselet):
    """Parses an expression enclosed in parentheses."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        """
        Parses a grouped expression.
        """
        # THE FIX: Consume the opening parenthesis '(' immediately to prevent
        # an infinite recursion loop.
        parser.next_token()

        # Now, parse the expression inside the parentheses.
        expression = parser.parse_expression(Precedence.LOWEST)

        # Expect a closing parenthesis.
        if not parser.expect_peek(TokenType.RPAREN):
            raise ParserError("Expected ')' after expression.", expression.token)

        return expression
