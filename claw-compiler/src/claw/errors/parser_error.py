"""
Defines the specific error type for parsing errors.
"""
from .base import ClawError
from ..tokens import Token

class ParserError(ClawError):
    """
    Represents an error that occurs during the parsing phase of compilation.

    This error is raised when the sequence of tokens does not conform to the
    expected grammar rules of the NyanLang language.
    """
    def __init__(self, message: str, token: Token):
        """
        Initializes a ParserError using a token to extract the location.

        Args:
            message: The description of the error.
            token: The token at or near which the error occurred. Its line
                   and column numbers are used for reporting the error location.
        """
        super().__init__(message, token.line, token.column)
