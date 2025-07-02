"""
Defines the parselet for handling if-else expressions.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import TokenType, Token
from ...errors import ParserError
from ..interfaces import PrefixParselet
from ..precedence import Precedence
# The FIX: Import the external, reusable block parser.
from ..statements.block import parse_block_statement

class IfParselet(PrefixParselet):
    """Parses an if-else expression."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        """
        Parses an if-expression.
        Grammar: 'if' Expression '{' ... '}' ['else' '{' ... '}']
        """
        # The current token is 'if'. We need to advance to parse the condition.
        parser.next_token()
        condition = parser.parse_expression(Precedence.LOWEST)

        if not parser.expect_peek(TokenType.LBRACE):
            raise ParserError("Expected '{' after if condition.", condition.token)
        
        # The FIX: Call the correct, external helper function.
        consequence = parse_block_statement(parser)

        alternative: ast.BlockStatement | None = None
        # After parsing the block, the current token will be '}'.
        # We need to check the *next* token for 'else'.
        if parser.peek_is(TokenType.ELSE):
            parser.next_token() # Consume '}'
            parser.next_token() # Consume 'else'
            
            if not parser.current_is(TokenType.LBRACE):
                assert parser.current_token is not None
                raise ParserError("Expected '{' after 'else' keyword.", parser.current_token)
            
            alternative = parse_block_statement(parser)

        return ast.IfExpression(
            token=token,
            condition=condition,
            consequence=consequence,
            alternative=alternative
        )
