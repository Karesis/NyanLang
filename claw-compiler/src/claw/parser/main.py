"""
Defines the main Parser class, which serves as the central dispatcher for
the parsing process.
"""
from __future__ import annotations

from ..tokens import Token, TokenType
from ..lexer import Lexer
from .. import ast
from ..errors import ParserError
from .precedence import Precedence
from .interfaces import PrefixParselet, InfixParselet

# Use the user's improved naming convention to avoid keyword conflicts.
from .statements.let import parse_let_statement
from .statements._return import parse_return_statement
from .statements._break import parse_break_statement
from .statements._continue import parse_continue_statement
from .statements.flow import parse_flow_statement
from .statements.definition import parse_def_statement

class Parser:
    def __init__(self,
                 lexer: Lexer,
                 prefix_parselets: dict[TokenType, PrefixParselet],
                 infix_parselets: dict[TokenType, InfixParselet]):
        self._lexer = lexer
        self._errors: list[ParserError] = []
        self._prefix_parselets = prefix_parselets
        self._infix_parselets = infix_parselets
        self.current_token: Token | None = None
        self.peek_token: Token | None = None
        self.next_token()
        self.next_token()

    @property
    def errors(self) -> list[ParserError]:
        return self._errors

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self._lexer.next_token()

    def current_is(self, token_type: TokenType) -> bool:
        return self.current_token is not None and self.current_token.token_type == token_type

    def peek_is(self, token_type: TokenType) -> bool:
        return self.peek_token is not None and self.peek_token.token_type == token_type

    def expect_peek(self, token_type: TokenType) -> bool:
        if self.peek_is(token_type):
            self.next_token()
            return True
        return False

    def parse_program(self) -> ast.Program:
        """Parses the entire program and returns the root AST node."""
        program = ast.Program(statements=[])
        while self.current_token and self.current_token.token_type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt:
                    program.statements.append(stmt)

            except ParserError as e:
                self._errors.append(e)
                self._synchronize()
                continue
            # The main loop should always advance the token after
            # attempting to parse a statement, regardless of what it was.
            self.next_token()
        return program

    def _synchronize(self) -> None:
        """
        An internal error recovery helper. It advances tokens until it finds a
        likely start of a new statement.
        """
        # Advance at least once to break the infinite loop when an
        # error occurs on a recovery token itself.
        self.next_token()
        # Corrected: Removed TokenType.LET as it's not a keyword in NyanLang.
        RECOVERY_TOKENS: set[TokenType] = {
            TokenType.RET,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.AT,
            TokenType.DEF,
            TokenType.IF,
            TokenType.LOOP,
            TokenType.WHILE,
        }
        while self.current_token and self.current_token.token_type not in RECOVERY_TOKENS:
            if self.current_token.token_type == TokenType.EOF:
                return
            self.next_token()

    def parse_statement(self) -> ast.Statement | None:
        if self.current_token is None:
            return None
        token_type = self.current_token.token_type
        if token_type == TokenType.RET:
             return parse_return_statement(self)
        elif token_type == TokenType.BREAK:
             return parse_break_statement(self)
        elif token_type == TokenType.CONTINUE:
             return parse_continue_statement(self)
        elif token_type == TokenType.AT:
             return parse_flow_statement(self)
        elif token_type == TokenType.DEF:
             return parse_def_statement(self)
        elif token_type == TokenType.IDENTIFIER and self.peek_is(TokenType.COLON):
            return parse_let_statement(self)
        else:
            return self.parse_expression_statement()

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        expression = self.parse_expression(Precedence.LOWEST)
        if self.peek_is(TokenType.SEMICOLON):
            self.next_token()
        return ast.ExpressionStatement(expression=expression)

    def parse_expression(self, precedence: Precedence) -> ast.Expression:
        token = self.current_token
        assert token is not None, "Current token should not be None."
        prefix_parselet = self._prefix_parselets.get(token.token_type)
        if prefix_parselet is None:
            raise ParserError(f"Unexpected token '{token.literal}' found when expecting an expression.", token)
        left_expression = prefix_parselet.parse(self, token)
        while self.peek_token and precedence < self._peek_precedence():
            if self.peek_token.token_type not in self._infix_parselets:
                return left_expression
            infix_parselet = self._infix_parselets[self.peek_token.token_type]
            self.next_token()
            assert self.current_token is not None
            left_expression = infix_parselet.parse(self, left_expression, self.current_token)
        return left_expression

    def _peek_precedence(self) -> Precedence:
        if self.peek_token:
            infix_parselet = self._infix_parselets.get(self.peek_token.token_type)
            if infix_parselet:
                return infix_parselet.precedence
        return Precedence.LOWEST
