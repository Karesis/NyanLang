# src/claw/parser/statement_parser.py

"""
Defines the StatementParser, responsible for parsing all statement types
in the Nyan language.
"""
from __future__ import annotations

# Used for type hinting to avoid circular imports at runtime.
from typing import TYPE_CHECKING

from ..ast import (
    BlockStatement,
    Expression,
    ExpressionStatement,
    FunctionDeclaration,
    Identifier,
    LetStatement,
    ReturnStatement,
    Statement,
    StructDefinition,
    TypeNode,
)
from ..token import TokenType
from .utils import Precedence

# This check is True only for type checkers, not at runtime.
if TYPE_CHECKING:
    from .main import Parser


class StatementParser:
    """
    Parses statement-level constructs.

    This class is a sub-parser of the main Parser and is responsible for
    all logic related to parsing statements like `let`, `ret`, `def`, etc.
    """

    def __init__(self, parser: Parser) -> None:
        """
        Initializes the StatementParser.

        Args:
            parser: A reference to the main Parser instance to access its
                    shared state (token stream, errors) and helper methods.
        """
        self.parser = parser

    def parse_statement(self) -> Statement | None:
        """
        Dispatches to the appropriate parsing method based on the current token.
        This is the entry point for all statement parsing.
        """
        token_type = self.parser.cur_token.type

        if token_type == TokenType.DEF:
            return self.parse_struct_definition()
        # Note: Function declarations are not handled here directly, as they
        # might be part of more complex grammar rules later.
        # Let's assume for now they are parsed via specific entry points if needed.
        # Or handled based on context. For now, we simplify.
        if token_type == TokenType.RET:
            return self.parse_return_statement()
        if token_type == TokenType.IDENT:
            # An identifier could start a let-statement or a function call statement.
            if self.parser.peek_token.type == TokenType.COLON:
                return self.parse_let_statement()

        # If no specific statement keyword is matched, parse it as an expression statement.
        return self.parse_expression_statement()

    def parse_let_statement(self) -> LetStatement | None:
        """Parses a let statement, e.g., 'x: i32 = 5;'."""
        let_token = self.parser.cur_token  # The identifier token
        name = Identifier(token=let_token, value=let_token.literal)

        if not self.parser.expect_peek(TokenType.COLON):
            return None

        self.parser.next_token()  # Consume the type identifier
        type_node = TypeNode(token=self.parser.cur_token, name=self.parser.cur_token.literal)

        value: Expression | None = None
        if self.parser.peek_token.type == TokenType.ASSIGN:
            self.parser.next_token()  # Consume '='
            self.parser.next_token()  # Move to the start of the expression

            # Delegate expression parsing to the ExpressionParser
            value = self.parser.expressions.parse_expression(Precedence.LOWEST)
            if value is None:
                self.parser.errors.append("Invalid expression in let statement")
                return None

        if self.parser.peek_token.type == TokenType.SEMICOLON:
            self.parser.next_token()

        return LetStatement(token=let_token, name=name, type=type_node, value=value)

    def parse_return_statement(self) -> ReturnStatement | None:
        """Parses a return statement, e.g., 'ret 10;'."""
        ret_token = self.parser.cur_token
        self.parser.next_token()  # Consume 'ret'

        # Delegate to the expression parser to get the return value.
        return_value = self.parser.expressions.parse_expression(Precedence.LOWEST)

        if self.parser.peek_token.type == TokenType.SEMICOLON:
            self.parser.next_token()

        # Create the immutable AST node after all parts have been parsed.
        return ReturnStatement(token=ret_token, return_value=return_value)

    def parse_expression_statement(self) -> ExpressionStatement | None:
        """Parses a statement that consists of a single expression."""
        expr_token = self.parser.cur_token

        # Delegate the entire expression parsing.
        expression = self.parser.expressions.parse_expression(Precedence.LOWEST)
        if expression is None:
            # The expression parser should have already logged an error.
            return None

        # Create the statement node after the expression has been fully parsed.
        stmt = ExpressionStatement(token=expr_token, expression=expression)

        # Optionally consume a trailing semicolon.
        if self.parser.peek_token.type == TokenType.SEMICOLON:
            self.parser.next_token()

        return stmt

    def parse_block_statement(self) -> BlockStatement:
        """Parses a block of statements enclosed in '{}'."""
        block_token = self.parser.cur_token  # The '{' token
        statements: list[Statement] = []
        self.parser.next_token()  # Consume '{'

        while (self.parser.cur_token.type != TokenType.RBRACE and
               self.parser.cur_token.type != TokenType.EOF):
            stmt = self.parse_statement()  # Recursively parse inner statement
            if stmt is not None:
                statements.append(stmt)
            self.parser.next_token()  # Advance past the parsed statement

        return BlockStatement(token=block_token, statements=statements)

    # NOTE: Function and Struct parsing logic can be complex.
    # The following are simplified implementations based on the provided code.

    def _parse_return_annotation(self) -> tuple[TypeNode, FieldList] | None:
        """
        Parses a function's return annotation, which can be simple or compound.
        
        A return annotation consists of a primary return type, and an optional
        set of captured fields for compound returns.
        
        e.g., "-> i32" or "-> i32{x: i32}"
        
        Returns:
            A tuple containing (primary_return_type, capture_fields), or None on failure.
        """
        # Expect '->'
        if not self.parser.expect_peek(TokenType.ARROW):
            return None

        # Expect a primary return type, e.g., 'i32'
        if not self.parser.expect_peek(TokenType.IDENT):
            self.parser.errors.append("Expected a return type name after '->'")
            return None
        
        primary_return_type = TypeNode(
            token=self.parser.cur_token, name=self.parser.cur_token.literal
        )

        # Now, check for an optional compound return part '{...}'
        capture_fields: FieldList = []
        if self.parser.peek_token.type == TokenType.LBRACE:
            # This is a compound return type! We can reuse our field parsing logic.
            self.parser.next_token()  # Consume '{'
            
            # Re-use the logic for parsing fields inside a struct
            parsed_fields = self.parse_struct_fields()
            if parsed_fields is None:
                # Error was logged inside parse_struct_fields
                return None
            capture_fields = parsed_fields

        return primary_return_type, capture_fields

    def parse_function_declaration(self, is_flow: bool) -> FunctionDeclaration | None:
        """
        Parses a function or a flow declaration.
        
        Handles normal functions: `add(a: i32) -> i32 { ... }`
        Handles flows: `@main { ... }`
        And compound returns: `... -> i32{x: i32} { ... }`
        """
        func_name_token = self.parser.cur_token # e.g., 'add' or '@'
        
        # For flows like @main, the name is the next token.
        if is_flow:
            if not self.parser.expect_peek(TokenType.IDENT):
                self.parser.errors.append("Expected a name after '@' for flow definition.")
                return None
        
        name = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)

        # --- Parameters ---
        params: FieldList = []
        # Normal functions must have '()', flows can omit them.
        if self.parser.peek_token.type == TokenType.LPAREN:
            self.parser.next_token()  # Consume '('
            parsed_params = self.parse_function_parameters()
            if parsed_params is None: return None
            params = parsed_params
        elif not is_flow:
            # If it's not a flow, parentheses for parameters are mandatory.
            self.parser.errors.append(f"Expected '(' after function name '{name.value}'")
            return None

        # --- Return Type Annotation ---
        return_type: TypeNode | None = None
        capture_fields: FieldList = []
        
        # Return annotation is mandatory for normal functions, optional for flows.
        if self.parser.peek_token.type == TokenType.ARROW:
            # Use our new helper method to parse the whole return annotation!
            type_info = self._parse_return_annotation()
            if type_info is None:
                return None  # Parsing failed
            return_type, capture_fields = type_info
        elif not is_flow:
            self.parser.errors.append(f"Expected '->' for return type annotation in function '{name.value}'")
            return None

        # If it's a flow and has no return type, we can assign a default (e.g., void)
        # during semantic analysis. For now, the parser accepts its absence.
        if is_flow and return_type is None:
            # Create a dummy void TypeNode for flows without explicit returns.
            # The token is the function name token, which is a reasonable anchor.
            return_type = TypeNode(token=func_name_token, name="void")

        # --- Body ---
        if not self.parser.expect_peek(TokenType.LBRACE):
            return None
        
        body = self.parse_block_statement()
        
        return FunctionDeclaration(
            token=func_name_token,
            name=name,
            params=params,
            return_type=return_type,
            capture_fields=capture_fields,
            body=body,
            is_flow=is_flow,
        )

    def parse_function_parameters(self) -> list[tuple[Identifier, TypeNode]] | None:
        """Parses a list of typed parameters from within parentheses."""
        params: list[tuple[Identifier, TypeNode]] = []

        # Case 1: Empty parameter list, e.g., "()"
        if self.parser.peek_token.type == TokenType.RPAREN:
            self.parser.next_token()  # Consume ')'
            return params

        # Case 2: At least one parameter
        self.parser.next_token()  # Consume the first parameter's identifier

        # -- Start of the robust loop pattern --
        while True:
            if self.parser.cur_token.type != TokenType.IDENT:
                self.parser.errors.append("Expected parameter name")
                return None
            
            ident = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)
            
            if not self.parser.expect_peek(TokenType.COLON): return None
            if not self.parser.expect_peek(TokenType.IDENT): return None  # Expecting type
            
            type_node = TypeNode(token=self.parser.cur_token, name=self.parser.cur_token.literal)
            params.append((ident, type_node))

            # After parsing one parameter, decide what to do next
            if self.parser.peek_token.type == TokenType.RPAREN:
                # End of list, consume ')' and exit
                self.parser.next_token()
                break
            elif self.parser.peek_token.type == TokenType.COMMA:
                # More parameters to come, consume ',' and the next identifier
                self.parser.next_token()  # Consume ','
                self.parser.next_token()  # Consume the next parameter's identifier to start the loop again
            else:
                # Invalid token
                self.parser.peek_error(TokenType.RPAREN) # Or COMMA
                return None
        # -- End of the robust loop pattern --
                
        return params

    def parse_struct_definition(self) -> StructDefinition | None:
        """Parses a struct definition, e.g., 'def {f: T} S;'."""
        def_token = self.parser.cur_token  # 'def'

        if not self.parser.expect_peek(TokenType.LBRACE): return None

        fields = self.parse_struct_fields()
        if fields is None: return None # Error logged in sub-parser

        if not self.parser.expect_peek(TokenType.IDENT):
            self.parser.errors.append("Expected struct name after field definition.")
            return None

        name = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)

        if self.parser.peek_token.type == TokenType.SEMICOLON:
            self.parser.next_token()

        return StructDefinition(token=def_token, name=name, fields=fields)

    def parse_struct_fields(self) -> list[tuple[Identifier, TypeNode]] | None:
        """Parses a list of typed fields from within curly braces."""
        fields: list[tuple[Identifier, TypeNode]] = []

        # Assumes current token is '{'.
        if self.parser.peek_token.type == TokenType.RBRACE:
            self.parser.next_token() # Consume '}'
            return fields

        self.parser.next_token() # Consume first field name

        while True:
            if self.parser.cur_token.type != TokenType.IDENT:
                self.parser.errors.append("Expected field name.")
                return None

            ident = Identifier(token=self.parser.cur_token, value=self.parser.cur_token.literal)

            if not self.parser.expect_peek(TokenType.COLON): return None
            if not self.parser.expect_peek(TokenType.IDENT): return None

            type_node = TypeNode(token=self.parser.cur_token, name=self.parser.cur_token.literal)
            fields.append((ident, type_node))

            if self.parser.peek_token.type == TokenType.RBRACE:
                self.parser.next_token() # Consume '}'
                break

            if not self.parser.expect_peek(TokenType.COMMA): return None
            self.parser.next_token() # Consume next field name

        return fields
