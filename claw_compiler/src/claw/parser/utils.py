# src/claw/parser/utils.py

"""
Defines precedence levels and mappings for operators in the Nyan language.

This module is a crucial component of the Pratt parser, providing the necessary
data to determine how expressions with different operators should be grouped.
"""

from enum import IntEnum, auto

from ..token import TokenType


class Precedence(IntEnum):
    """
    Defines the precedence levels for operators.

    A higher integer value corresponds to a higher precedence.
    The order of declaration determines the integer value when using `auto()`.
    """
    _ = auto()  # Start auto-numbering from 1 for clarity (0 is often default)
    LOWEST      = auto()  # The lowest precedence for any operator
    EQUALS      = auto()  # Precedence for assignment (=)
    LESSGREATER = auto()  # Precedence for comparisons (<, >) (not yet used)
    SUM         = auto()  # Precedence for addition (+) and subtraction (-)
    PRODUCT     = auto()  # Precedence for multiplication (*) and division (/)
    PREFIX      = auto()  # Precedence for prefix operators (e.g., -x, !x)
    CALL        = auto()  # Precedence for function calls, e.g., myFunction(x)
    MEMBER      = auto()  # Precedence for member access, e.g., myStruct.field


# A mapping from token types to their corresponding precedence levels.
# This table is the heart of the Pratt parser's decision-making process.
precedences: dict[TokenType, Precedence] = {
    TokenType.ASSIGN:   Precedence.EQUALS,
    TokenType.PLUS:     Precedence.SUM,
    TokenType.MINUS:    Precedence.SUM,
    TokenType.SLASH:    Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN:   Precedence.CALL,
    TokenType.LBRACE:   Precedence.CALL,      # For struct literals, e.g., Point{...}
    TokenType.DOT:      Precedence.MEMBER,
}
