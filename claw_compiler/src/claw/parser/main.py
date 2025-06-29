# src/claw/parser/main.py

"""
Defines the main Parser for the Nyan language.

The Parser acts as a coordinator, delegating parsing tasks to specialized
sub-parsers for statements and expressions. It manages the shared state,
including the token stream and error collection.
"""

from __future__ import annotations

from ..ast import Program
from ..lexer import Lexer
from ..token import Token, TokenType
from .expression_parser import ExpressionParser
from .statement_parser import StatementParser
from .utils import Precedence, precedences


class Parser:
    """
    The main parser, acting as a coordinator for sub-parsers.

    This class does not contain specific parsing logic itself. Instead, it holds
    the shared state (token stream, errors) and provides helper methods that
    the sub-parsers (`StatementParser`, `ExpressionParser`) use to do their work.

    Attributes:
        lexer (Lexer): The lexer instance providing the token stream.
        errors (list[str]): A list of error messages accumulated during parsing.
        cur_token (Token): The current token being examined.
        peek_token (Token): The next token in the stream (one token lookahead).
        statements (StatementParser): The sub-parser responsible for statements.
        expressions (ExpressionParser): The sub-parser responsible for expressions.
    """
    cur_token: Token
    peek_token: Token
    statements: StatementParser
    expressions: ExpressionParser

    def __init__(self, lexer: Lexer) -> None:
        """
        Initializes the parser and primes it by loading the first two tokens.

        The parser requires a two-token lookahead (`cur_token` and `peek_token`)
        to support Pratt parsing, where decisions are made based on the
        precedence of the upcoming token.

        Args:
            lexer: An initialized Lexer instance.
        """
        self.lexer = lexer
        self.errors: list[str] = []

        # Prime the parser by loading the first two tokens.
        # This is necessary for the lookahead mechanism to work from the start.
        # Note: The original 'is None' check was removed because our Lexer's
        # `next_token` method is guaranteed to always return a Token instance.
        self.cur_token = self.lexer.next_token()
        self.peek_token = self.lexer.next_token()

        # Compose the sub-parsers, passing this main parser instance so they
        # can access shared state (tokens, errors) and helper methods.
        self.statements = StatementParser(self)
        self.expressions = ExpressionParser(self)

    # --- Core Token Helpers (used by all sub-parsers) ---

    def next_token(self) -> None:
        """Advances the token stream by one token."""
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_peek(self, t: TokenType) -> bool:
        """
        Asserts that the next token is of the expected type.

        If the peeked token matches the expected type, it consumes the token
        (advances the stream) and returns True. Otherwise, it records an error
        and returns False.

        Args:
            t: The expected TokenType.

        Returns:
            True if the token matched and was consumed, False otherwise.
        """
        if self.peek_token.type == t:
            self.next_token()
            return True
        self.peek_error(t)
        return False

    def peek_error(self, t: TokenType) -> None:
        """Records an error message for an unexpected peeked token."""
        msg = (
            f"expected next token to be {t.name}, "
            f"got {self.peek_token.type.name} instead"
        )
        self.errors.append(msg)

    def peek_precedence(self) -> Precedence:
        """Gets the precedence of the next (peek) token."""
        return precedences.get(self.peek_token.type, Precedence.LOWEST)

    def cur_precedence(self) -> Precedence:
        """Gets the precedence of the current token."""
        return precedences.get(self.cur_token.type, Precedence.LOWEST)

    # --- Top-Level Parsing Entry Point ---

    def parse_program(self) -> Program:
        """
        Parses the entire source code and returns the root AST node.

        This is the main entry point for the parsing process. It iterates through
        the token stream until EOF, delegating the parsing of each statement
        to the `StatementParser`.

        Returns:
            The root `Program` node of the generated AST.
        """
        program = Program(statements=[])

        while self.cur_token.type != TokenType.EOF:
            # Delegate statement parsing to the specialized sub-parser.
            stmt = self.statements.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)

            # Advancing the token is the responsibility of the main loop
            # after each statement is parsed.
            self.next_token()

        return program
