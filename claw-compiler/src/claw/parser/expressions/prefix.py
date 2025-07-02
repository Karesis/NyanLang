"""
Defines the parselet for handling prefix operators like '-' or '!'.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token
from ..interfaces import PrefixParselet
from ..precedence import Precedence

class PrefixOperatorParselet(PrefixParselet):
    """
    A generic parselet for handling any prefix operator.
    It parses the expression that follows the operator.
    """
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        """
        Parses a prefix expression.

        This method consumes the prefix operator token, then recursively calls
        the main expression parser for the operand that follows. The precedence
        level `Precedence.PREFIX` is passed to handle operator associativity
        correctly.
        """
        # THE FIX: Consume the prefix operator token (e.g., '-') to advance
        # the parser before parsing the operand.
        parser.next_token()

        # Now, parse the expression on the right-hand side.
        right_operand = parser.parse_expression(Precedence.PREFIX)

        return ast.PrefixExpression(
            token=token,
            operator=token.literal,
            right=right_operand
        )
