"""
Defines the parselet for handling mutable assignment, e.g., `z = 7`.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token
from ...errors import ParserError
from ..interfaces import InfixParselet
from ..precedence import Precedence

class AssignmentParselet(InfixParselet):
    """
    Parses a mutable assignment expression. The '=' token triggers this.
    """
    @property
    def precedence(self) -> Precedence:
        return Precedence.ASSIGN

    def parse(self, parser: 'Parser', left: ast.Expression, token: Token) -> ast.Expression:
        """
        Parses the right-hand side of the assignment.
        """
        # The left-hand side of an assignment must be a valid target,
        # such as an Identifier or a MemberAccessExpression.
        if not isinstance(left, (ast.Identifier, ast.MemberAccessExpression)):
            raise ParserError("Invalid assignment target.", token)

        # Before parsing the right-hand side, we must advance
        # the parser past the assignment operator token itself.
        parser.next_token()

        # The expression on the right is parsed with a slightly lower
        # precedence to handle cases like `a = b = c` correctly if we
        # decide to support right-associativity later.
        right = parser.parse_expression(Precedence(self.precedence - 1))

        return ast.AssignmentExpression(
            token=token,
            name=left, # `name` can be a simple Identifier or a complex MemberAccess
            value=right
        )
