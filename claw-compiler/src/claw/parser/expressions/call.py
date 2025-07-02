"""
Defines the parselet for handling function call expressions, e.g., `my_func(a, b)`.
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

class CallExpressionParselet(InfixParselet):
    """
    Parses a function call expression. The '(' token triggers this parselet
    in an infix position.
    """
    @property
    def precedence(self) -> Precedence:
        return Precedence.CALL

    def parse(self, parser: 'Parser', left: ast.Expression, token: Token) -> ast.Expression:
        """
        Parses the argument list of a function call.

        Args:
            parser: The main Parser instance.
            left: The expression for the function being called (e.g., an Identifier).
            token: The opening parenthesis '(' token.

        Returns:
            An `ast.CallExpression` node.
        """
        arguments = self._parse_argument_list(parser)
        return ast.CallExpression(token=token, function=left, arguments=arguments)

    def _parse_argument_list(self, parser: 'Parser') -> list[ast.Expression]:
        """Helper function to parse a comma-separated list of expressions."""
        args: list[ast.Expression] = []

        # Case 1: Empty argument list, correctly closed -> my_func()
        if parser.peek_is(TokenType.RPAREN):
            parser.next_token()  # Consume the ')'
            return args

        parser.next_token() # Consume '('

        # Before trying to parse the first argument, check if the
        # list is non-empty. If we are at the end of the file or at the
        # closing paren, there are no arguments to parse.
        if not parser.current_is(TokenType.EOF) and not parser.current_is(TokenType.RPAREN):
            args.append(parser.parse_expression(Precedence.LOWEST))

            # Parse subsequent arguments, which must be preceded by a comma.
            while parser.peek_is(TokenType.COMMA):
                parser.next_token()  # Consume the ','
                parser.next_token()  # Move to the start of the next expression
                args.append(parser.parse_expression(Precedence.LOWEST))

        # After the argument list, we expect a closing parenthesis.
        if not parser.expect_peek(TokenType.RPAREN):
            error_token: Token
            if args:
                error_token = args[-1].token
            else:
                assert parser.current_token is not None
                error_token = parser.current_token
            
            raise ParserError("Expected ')' after arguments.", error_token)

        return args
