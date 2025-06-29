# claw/token.py

"""
Defines the lexical tokens used in the Nyan programming language.

This module contains the definitions for token types, the Token data structure,
and utilities for handling language keywords.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of all possible token types."""

    # --- Special Types ---
    ILLEGAL = auto()  # An illegal character or sequence found in the source.
    EOF = auto()      # Represents the End Of File.

    # --- Identifiers + Literals ---
    IDENT = auto()    # e.g., add, foobar, x, y, ...
    INTEGER = auto()  # e.g., 123, 42

    # --- Operators ---
    ASSIGN = auto()   # =
    PLUS = auto()     # +
    MINUS = auto()    # -
    ASTERISK = auto() # *
    SLASH = auto()    # /

    # --- Delimiters ---
    COMMA = auto()    # ,
    SEMICOLON = auto()# ;
    COLON = auto()    # :
    DOT = auto()      # .
    AT = auto()       # @

    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACE = auto()   # {
    RBRACE = auto()   # }

    ARROW = auto()    # ->

    # --- Keywords ---
    RET = auto()      # 'ret' keyword
    DEF = auto()      # 'def' keyword


@dataclass(frozen=True)
class Token:
    """
    Represents a single token extracted from the source code by the lexer.

    Attributes:
        type: The category of the token (e.g., IDENT, INTEGER, PLUS).
        literal: The actual string value of the token from the source code.
    """
    type: TokenType
    literal: str

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the token."""
        return f"Token(type={self.type.name}, literal='{self.literal}')"


# A mapping of keyword strings to their corresponding TokenType.
# This is used by the lexer to distinguish keywords from regular identifiers.
keywords: dict[str, TokenType] = {
    "ret": TokenType.RET,
    "def": TokenType.DEF,
}


def lookup_ident(ident: str) -> TokenType:
    """
    Checks if a given identifier string is a keyword.

    Args:
        ident: The identifier string to check.

    Returns:
        The corresponding keyword TokenType if it is a keyword,
        otherwise returns TokenType.IDENT.
    """
    return keywords.get(ident, TokenType.IDENT)
