"""
Exposes all compiler error classes for easy and consistent importing.

This allows other parts of the compiler to import errors like this:
    from claw.errors import ParserError, LexerError
"""
from .base import ClawError
from .lexer_error import LexerError
from .parser_error import ParserError

__all__ = ["ClawError", "LexerError", "ParserError"]
