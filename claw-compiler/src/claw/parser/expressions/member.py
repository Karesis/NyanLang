"""
Defines the parselet for handling member access, e.g., `my_object.property`.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token, TokenType
from ...errors import ParserError
from ..interfaces import InfixParselet
from ..precedence import Precedence

class MemberAccessParselet(InfixParselet):
    """
    Parses a member access expression. The '.' token triggers this parselet.
    """
    @property
    def precedence(self) -> Precedence:
        return Precedence.MEMBER

    def parse(self, parser: 'Parser', left: ast.Expression, token: Token) -> ast.Expression:
        """
        Parses the property name after the '.' operator.
        """

        if parser.peek_is(TokenType.EOF):
            raise ParserError("Unexpected end of file after '.'.", token)
        
        # After the '.', we expect an identifier for the property name.
        if not parser.peek_is(TokenType.IDENTIFIER):
            raise ParserError("Expected property name after '.'.", token)

        parser.next_token() # Consume the property name token
        property_name_token = parser.current_token
        
        assert property_name_token is not None
        
        property_identifier = ast.Identifier(
            token=property_name_token,
            value=property_name_token.literal
        )

        return ast.MemberAccessExpression(
            token=token,
            object=left,
            property=property_identifier
        )
