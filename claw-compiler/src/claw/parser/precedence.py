"""
Defines the operator precedence levels for the Pratt parser.

Each level is assigned an integer value. Higher values indicate higher
precedence, meaning the operator will be bound to its operands more tightly.
"""
from enum import IntEnum

class Precedence(IntEnum):
    """
    An enumeration of operator precedence levels, from lowest to highest.
    """
    LOWEST = 0
    # Precedence for assignment expressions like 'z = 7'.
    # Note: 'z := 8' is a statement, not an expression, so it's handled differently.
    ASSIGN = 1
    EQUALS = 2       # ==, !=
    LESSGREATER = 3  # >, <, >=, <=
    SUM = 4          # +, -
    PRODUCT = 5      # *, /
    PREFIX = 6       # -x or !x
    CALL = 7         # myFunction(x)
    MEMBER = 8       # object.property
