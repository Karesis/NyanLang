"""
Defines the parselets for handling literal expressions like identifiers and numbers.
"""
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..main import Parser # pragma: no cover

from ... import ast
from ...tokens import Token
from ...errors import ParserError
from ..interfaces import PrefixParselet

class IdentifierParselet(PrefixParselet):
    """Parses an identifier token into an Identifier AST node."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        return ast.Identifier(token=token, value=token.literal)

class IntegerLiteralParselet(PrefixParselet):
    """Parses an integer token into an IntegerLiteral AST node."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        try:
            value = int(token.literal)
            return ast.IntegerLiteral(token=token, value=value)
        except ValueError:
            raise ParserError(f"Could not parse '{token.literal}' as an integer.", token)

class FloatLiteralParselet(PrefixParselet):
    """Parses a float token into a FloatLiteral AST node."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        try:
            value = float(token.literal)
            return ast.FloatLiteral(token=token, value=value)
        except ValueError:
            raise ParserError(f"Could not parse '{token.literal}' as a float.", token)

class StringLiteralParselet(PrefixParselet):
    """Parses a string token into a StringLiteral AST node."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        # The lexer already handled escape sequences and removed the quotes.
        return ast.StringLiteral(token=token, value=token.literal)

class BooleanLiteralParselet(PrefixParselet):
    """Parses a boolean token (true/false) into a BooleanLiteral AST node."""
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        # The lexer guarantees the literal is either "true" or "false".
        value = (token.literal == "true")
        return ast.BooleanLiteral(token=token, value=value)
