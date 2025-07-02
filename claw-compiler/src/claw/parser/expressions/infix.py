"""
Defines the generic parselet for handling infix binary operators like '+', '-', etc.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token
from ..interfaces import InfixParselet
from ..precedence import Precedence

class InfixOperatorParselet(InfixParselet):
    """
    A generic parselet for handling any infix operator. It uses the operator's
    precedence to correctly handle associativity.
    """
    def __init__(self, precedence: Precedence):
        self._precedence = precedence

    @property
    def precedence(self) -> Precedence:
        return self._precedence

    def parse(self, parser: 'Parser', left: ast.Expression, token: Token) -> ast.Expression:
        """
        Parses an infix expression.

        For an expression like "a + b", this method is triggered by the "+".
        The "a" is passed in as the `left` argument. This method then calls
        the main expression parser to parse the right-hand side ("b"), using
        its own precedence to manage operator associativity.
        """
        # THE FIX: Before parsing the right-hand side, we must advance
        # the parser past the infix operator token itself.
        parser.next_token()
        
        right = parser.parse_expression(self.precedence)

        return ast.InfixExpression(
            token=token,
            left=left,
            operator=token.literal,
            right=right
        )
