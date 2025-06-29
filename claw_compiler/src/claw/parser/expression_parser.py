# src/claw/parser/expression_parser.py

"""
Defines the ExpressionParser, responsible for parsing all expression types.
This module contains the core implementation of the Pratt parsing algorithm.
"""
from __future__ import annotations

from collections.abc import Callable

# Used for type hinting to avoid circular imports at runtime.
from typing import TYPE_CHECKING

from ..ast import (
    AssignmentExpression,
    CallExpression,
    Expression,
    Identifier,
    InfixExpression,
    IntegerLiteral,
    MemberAccessExpression,
    PrefixExpression,
    StructLiteral,
)
from ..token import TokenType
from .utils import Precedence

# This check is True only for type checkers, not at runtime.
if TYPE_CHECKING:
    from .main import Parser

# Type aliases for the function signatures in the Pratt parser's dispatch tables.
PrefixParseFn = Callable[[], Expression | None]
InfixParseFn = Callable[[Expression], Expression | None]


class ExpressionParser:
    """
    Parses expression-level constructs using a Pratt parser implementation.

    This sub-parser is instantiated by the main Parser. It uses two dispatch
    tables, `prefix_parse_fns` and `infix_parse_fns`, to handle different
    tokens based on whether they appear in a prefix or infix context.
    """

    def __init__(self, parser: Parser) -> None:
        """
        Initializes the ExpressionParser and registers all parsing functions.
        """
        self.parser = parser

        # The core of the Pratt parser: dispatch tables.
        self.prefix_parse_fns: dict[TokenType, PrefixParseFn] = {}
        self.infix_parse_fns: dict[TokenType, InfixParseFn] = {}

        # Register all prefix parsing functions.
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INTEGER, self.parse_integer_literal)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)

        # Register all infix parsing functions.
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.ASSIGN, self.parse_assignment_expression)
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACE, self.parse_struct_literal)
        self.register_infix(TokenType.DOT, self.parse_member_access_expression)

    def register_prefix(self, tt: TokenType, fn: PrefixParseFn) -> None:
        """Registers a function for parsing a prefix expression."""
        self.prefix_parse_fns[tt] = fn

    def register_infix(self, tt: TokenType, fn: InfixParseFn) -> None:
        """Registers a function for parsing an infix expression."""
        self.infix_parse_fns[tt] = fn

    def parse_expression(self, precedence: Precedence) -> Expression | None:
        """
        The core driver of the Pratt parser.

        It works by first parsing a prefix expression, then entering a loop
        that continues as long as the next token is an infix operator with
        a higher precedence than the current context (`precedence`).
        """
        prefix_fn = self.prefix_parse_fns.get(self.parser.cur_token.type)
        if prefix_fn is None:
            self.parser.errors.append(
                f"no prefix parse function for {self.parser.cur_token.type.name} found"
            )
            return None

        left_exp = prefix_fn()
        if left_exp is None:
            # Error should have been logged in the specific parsing function.
            return None

        while (self.parser.peek_token.type != TokenType.SEMICOLON and
               precedence < self.parser.peek_precedence()):

            infix_fn = self.infix_parse_fns.get(self.parser.peek_token.type)
            if infix_fn is None:
                # Not an infix operator, or an operator we can't handle here.
                # End the expression here.
                return left_exp

            self.parser.next_token()

            left_exp = infix_fn(left_exp)
            if left_exp is None:
                # Error should have been logged in the infix function.
                return None

        return left_exp

    # --- Prefix-parsing functions ---

    def parse_identifier(self) -> Identifier:
        """Parses an identifier, which is just the current token."""
        return Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)

    def parse_integer_literal(self) -> IntegerLiteral | None:
        """Parses an integer literal, converting its value from string to int."""
        token = self.parser.cur_token
        try:
            value = int(token.literal)
            return IntegerLiteral(token=token, value=value)
        except ValueError:
            self.parser.errors.append(f"could not parse '{token.literal}' as integer")
            return None

    def parse_prefix_expression(self) -> PrefixExpression | None:
        """Parses a prefix expression, e.g., '-5'."""
        token = self.parser.cur_token
        self.parser.next_token()

        right = self.parse_expression(Precedence.PREFIX)
        if right is None:
            return None

        return PrefixExpression(token=token, operator=token.literal, right=right)

    def parse_grouped_expression(self) -> Expression | None:
        """Parses a grouped expression, e.g., '(1 + 2)'."""
        self.parser.next_token()  # Consume '('
        exp = self.parse_expression(Precedence.LOWEST)
        if not self.parser.expect_peek(TokenType.RPAREN):
            return None
        return exp

    # --- Infix-parsing functions ---

    def parse_infix_expression(self, left: Expression) -> InfixExpression | None:
        """Parses a generic infix expression, e.g., 'left + right'."""
        token = self.parser.cur_token
        precedence = self.parser.cur_precedence()
        self.parser.next_token()

        right = self.parse_expression(precedence)
        if right is None:
            return None

        return InfixExpression(token=token, left=left, operator=token.literal, right=right)

    def parse_call_expression(self, function: Expression) -> CallExpression | None:
        """Parses a function call, e.g., 'add(1, 2)'."""
        call_token = self.parser.cur_token  # The '(' token
        arguments = self.parse_call_arguments()
        if arguments is None:
            return None

        return CallExpression(token=call_token, function=function, arguments=arguments)

    def parse_call_arguments(self) -> list[Expression] | None:
        """Parses a comma-separated list of arguments inside parentheses."""
        args: list[Expression] = []

        if self.parser.peek_token.type == TokenType.RPAREN:
            self.parser.next_token()  # Consume ')'
            return args

        self.parser.next_token()  # Move to the first argument's start token

        # Parse the first argument
        first_arg = self.parser.expressions.parse_expression(Precedence.LOWEST)
        if first_arg is None: return None
        args.append(first_arg)

        # Parse subsequent arguments
        while self.parser.peek_token.type == TokenType.COMMA:
            self.parser.next_token()  # Consume ','
            self.parser.next_token()  # Move to the next argument's start token

            next_arg = self.parser.expressions.parse_expression(Precedence.LOWEST)
            if next_arg is None: return None
            args.append(next_arg)

        if not self.parser.expect_peek(TokenType.RPAREN):
            return None

        return args

    def parse_assignment_expression(self, left: Expression) -> AssignmentExpression | None:
        """Parses an assignment, e.g., 'x = 5'."""
        if not isinstance(left, (Identifier, MemberAccessExpression)):
            self.parser.errors.append("Invalid assignment target. Must be an identifier or member access.")
            return None

        token = self.parser.cur_token
        precedence = self.parser.cur_precedence()
        self.parser.next_token()

        value = self.parse_expression(precedence)
        if value is None:
            return None

        return AssignmentExpression(token=token, left=left, value=value)

    def parse_member_access_expression(self, left: Expression) -> MemberAccessExpression | None:
        """Parses a member access, e.g., 'my_struct.field'."""
        token = self.parser.cur_token  # The '.' token

        # We expect an identifier after the dot.
        if not self.parser.expect_peek(TokenType.IDENT):
            return None

        field = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)
        return MemberAccessExpression(token=token, object=left, field=field)

    def parse_struct_literal(self, type_name: Expression) -> StructLiteral | None:
        """Parses a struct literal, e.g., 'Point{x: 1, y: 2}'."""
        literal_token = self.parser.cur_token  # The '{' token
        if not isinstance(type_name, Identifier):
            self.parser.errors.append(f"Expected a struct name before '{{', got {type_name}")
            return None

        members: list[tuple[Identifier, Expression]] = []

        if self.parser.peek_token.type == TokenType.RBRACE:
            self.parser.next_token()  # Consume '}'
            return StructLiteral(token=literal_token, type_name=type_name, members=members)

        self.parser.next_token()  # Consume first member name

        while True:
            if self.parser.cur_token.type != TokenType.IDENT:
                self.parser.errors.append("Expected member name in struct literal.")
                return None

            ident = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)

            if not self.parser.expect_peek(TokenType.COLON): return None

            self.parser.next_token() # Move to the start of the value expression

            value = self.parse_expression(Precedence.LOWEST)
            if value is None: return None

            members.append((ident, value))

            if self.parser.peek_token.type == TokenType.RBRACE:
                self.parser.next_token()  # Consume '}'
                break

            if not self.parser.expect_peek(TokenType.COMMA): return None
            self.parser.next_token() # Consume next member name for the loop

        return StructLiteral(token=literal_token, type_name=type_name, members=members)
