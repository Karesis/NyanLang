"""
Defines the core interfaces for the parselets used by the Pratt parser.

A "parselet" is a small class responsible for parsing a specific language
construct. This pattern allows for a modular and extensible parser design.
We define two main types of parselets:
- PrefixParselet: For tokens that start an expression (e.g., numbers, identifiers, '-').
- InfixParselet: For tokens that appear between two expressions (e.g., '+', '*', '==').
"""
from __future__ import annotations
import typing
from abc import ABC, abstractmethod

# This is a common pattern to avoid circular import errors.
# The `Parser` class needs to know about the parselets, and the parselets
# need to know the type of the `Parser` object they receive.
# `if typing.TYPE_CHECKING:` ensures this import only runs during static analysis.
if typing.TYPE_CHECKING:
    from .main import Parser # pragma: no cover

from .. import ast
from ..tokens import Token
from .precedence import Precedence

class PrefixParselet(ABC):
    """
    Interface for parsing expressions that begin with a specific token type.
    For example, an integer `5`, an identifier `x`, or a prefix operator `-`.
    """
    @abstractmethod
    def parse(self, parser: 'Parser', token: Token) -> ast.Expression:
        """
        Parses the expression.

        Args:
            parser: The main Parser instance, used to recursively call parsing functions.
            token: The token that triggered this parselet.

        Returns:
            The resulting Expression AST node.
        """
        raise NotImplementedError

class InfixParselet(ABC):
    """
    Interface for parsing expressions where a token appears between two operands.
    For example, the `+` in `a + b` or the `(` in `my_func(a)`.
    """
    @abstractmethod
    def parse(self, parser: 'Parser', left: ast.Expression, token: Token) -> ast.Expression:
        """
        Parses the rest of the expression, using the `left` expression as the
        left-hand operand.

        Args:
            parser: The main Parser instance.
            left: The expression node that was parsed just before this infix token.
            token: The infix token that triggered this parselet.

        Returns:
            The resulting Expression AST node that combines `left` and the right-hand side.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def precedence(self) -> Precedence:
        """
        Returns the precedence of this infix operator. This is crucial for the
        Pratt parser to decide whether to continue parsing or to stop.
        """
        raise NotImplementedError
