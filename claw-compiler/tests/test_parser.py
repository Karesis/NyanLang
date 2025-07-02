"""
Tests for the Parser, ensuring it correctly constructs an AST from tokens.
"""
import typing
import pytest
from claw.lexer import Lexer
from claw.parser import create_parser, Parser
from claw import ast
from claw.errors import ParserError

# --- Helper Functions for Cleaner Tests ---

def check_parser_errors(parser: Parser) -> None:
    """Fails the test if the parser encountered any errors."""
    if not parser.errors:
        return
    messages = "\n".join([str(e) for e in parser.errors])
    pytest.fail(f"Parser encountered {len(parser.errors)} errors:\n{messages}")

def _check_integer_literal(expr: ast.Expression, value: int):
    assert isinstance(expr, ast.IntegerLiteral)
    assert expr.value == value
    assert expr.token_literal() == str(value)

def _check_identifier(expr: ast.Expression, value: str):
    assert isinstance(expr, ast.Identifier)
    assert expr.value == value
    assert expr.token_literal() == value

def _check_boolean_literal(expr: ast.Expression, value: bool):
    assert isinstance(expr, ast.BooleanLiteral)
    assert expr.value == value
    assert expr.token_literal() == str(value).lower()

def _check_infix_expression(expr: ast.Expression, left: typing.Any, operator: str, right: typing.Any):
    """
    Helper function to check the contents of an InfixExpression node.
    """
    assert isinstance(expr, ast.InfixExpression)
    assert expr.operator == operator
    
    # Check for bool BEFORE int, because isinstance(True, int) is True.
    if isinstance(left, bool):
        _check_boolean_literal(expr.left, left)
    elif isinstance(left, int):
        _check_integer_literal(expr.left, left)
    elif isinstance(left, str):
        _check_identifier(expr.left, left)
    else:
        pytest.fail(f"Unsupported type for left operand check: {type(left)}")
    
    # Apply the same fix for the right operand.
    if isinstance(right, bool):
        _check_boolean_literal(expr.right, right)
    elif isinstance(right, int):
        _check_integer_literal(expr.right, right)
    elif isinstance(right, str):
        _check_identifier(expr.right, right)
    else:
        pytest.fail(f"Unsupported type for right operand check: {type(right)}")

# --- Test Cases ---

def test_let_statement():
    source_code = "x: i32 := 5"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.LetStatement)
    assert stmt.name.value == "x"
    assert not stmt.mutable
    assert isinstance(stmt.value, ast.IntegerLiteral)
    assert stmt.value.value == 5

def test_mutable_let_statement():
    """Tests parsing a mutable variable declaration."""
    source_code = "y: ~f64"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.LetStatement)
    assert stmt.name.value == "y"
    assert stmt.mutable
    assert stmt.value is None
    assert isinstance(stmt.value_type, ast.MutableType)
    assert isinstance(stmt.value_type.base_type, ast.SimpleType)
    assert stmt.value_type.base_type.token_literal() == "f64"

def test_return_statement():
    source_code = "ret 10"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ReturnStatement)
    assert isinstance(stmt.return_value, ast.IntegerLiteral)
    assert stmt.return_value.value == 10

def test_prefix_expression():
    source_code = "-15"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    expr = stmt.expression
    assert isinstance(expr, ast.PrefixExpression)
    assert expr.operator == "-"
    _check_integer_literal(expr.right, 15)
    # This covers PrefixExpression.token_literal
    assert expr.token_literal() == "-"
    # This covers ExpressionStatement.token_literal
    assert stmt.token_literal() == "-"

@pytest.mark.parametrize("source_code, left_value, operator, right_value", [
    ("5 + 5", 5, "+", 5),
    ("5 - 5", 5, "-", 5),
    ("5 * 5", 5, "*", 5),
    ("5 / 5", 5, "/", 5),
    ("5 > 5", 5, ">", 5),
    ("5 < 5", 5, "<", 5),
    ("5 == 5", 5, "==", 5),
    ("5 != 5", 5, "!=", 5),
    ("true == true", True, "==", True),
    ("foo != bar", "foo", "!=", "bar"),
])
def test_infix_expressions(source_code: str, left_value: typing.Any, operator: str, right_value: typing.Any):
    """Tests various simple infix expressions."""
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    _check_infix_expression(stmt.expression, left_value, operator, right_value)

@pytest.mark.parametrize("source_code, expected_str", [
    ("-a * b", "((-a) * b)"),
    ("a + b + c", "((a + b) + c)"),
    ("a + b * c", "(a + (b * c))"),
    ("(a + b) * c", "((a + b) * c)"),
    ("a + b / c", "(a + (b / c))"),
    ("add(a, b, 1, 2 * 3, 4 + 5)", "add(a, b, 1, (2 * 3), (4 + 5))"),
])
def test_operator_precedence_parsing(source_code: str, expected_str: str):
    """
    Tests operator precedence by checking the string representation of the AST.
    """
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    
    actual_str = str(program)
    assert actual_str == expected_str


def test_if_else_expression():
    """Tests parsing of an if-else expression."""
    source_code = "if x < y { x } else { y }"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    expr = stmt.expression
    assert isinstance(expr, ast.IfExpression)
    _check_infix_expression(expr.condition, "x", "<", "y")
    assert isinstance(expr.consequence, ast.BlockStatement)
    assert len(expr.consequence.statements) == 1
    cons_stmt = expr.consequence.statements[0]
    assert isinstance(cons_stmt, ast.ExpressionStatement)
    _check_identifier(cons_stmt.expression, "x")
    assert expr.alternative is not None
    assert isinstance(expr.alternative, ast.BlockStatement)
    assert len(expr.alternative.statements) == 1
    alt_stmt = expr.alternative.statements[0]
    assert isinstance(alt_stmt, ast.ExpressionStatement)
    _check_identifier(alt_stmt.expression, "y")

def test_function_call_expression():
    """Tests parsing a function call with multiple arguments."""
    source_code = "add(1, 2 * 3, 4 + 5)"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    expr = stmt.expression
    assert isinstance(expr, ast.CallExpression)
    _check_identifier(expr.function, "add")
    assert len(expr.arguments) == 3
    _check_integer_literal(expr.arguments[0], 1)
    _check_infix_expression(expr.arguments[1], 2, "*", 3)
    _check_infix_expression(expr.arguments[2], 4, "+", 5)

    assert expr.token_literal() == "("

def test_break_statement():
    """Tests parsing a simple break statement."""
    source_code = "break"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert str(program) == "break;"

def test_break_statement_with_value():
    """Tests parsing a break statement that returns a value."""
    source_code = "break 100"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert str(program) == "break 100;"

def test_continue_statement():
    """Tests parsing a simple continue (con) statement."""
    source_code = "con"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert str(program) == "con;"

# In tests/test_parser.py, add these new test functions at the end of the file.

def test_def_statement():
    """Tests parsing a struct definition with fields."""
    source_code = "def { x: i32, y: ~bool } Point"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.DefStatement)

    assert stmt.name.value == "Point"
    assert len(stmt.fields) == 2
    
    # Check fields
    field_names = [f.value for f in stmt.fields.keys()]
    assert "x" in field_names
    assert "y" in field_names

    # Check types
    x_type = next(t for f, t in stmt.fields.items() if f.value == "x")
    y_type = next(t for f, t in stmt.fields.items() if f.value == "y")
    
    assert isinstance(x_type, ast.SimpleType)
    assert x_type.token_literal() == "i32"
    
    assert isinstance(y_type, ast.MutableType)
    assert str(y_type) == "~bool"

    assert stmt.token_literal() == "def"
    assert str(stmt) == "def { x: i32, y: ~bool } Point"

def test_flow_statement():
    """Tests parsing a flow definition."""
    source_code = """
    @my_flow {
        x: i32 := 5
        ret x
    }
    """
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.FlowStatement)

    assert stmt.name.value == "my_flow"
    assert len(stmt.body.statements) == 2

    assert stmt.token_literal() == "@"
    assert str(stmt) == "@my_flow { x: i32 := 5ret x; }"

def test_member_access_expression():
    """Tests parsing a member access expression."""
    source_code = "my_obj.my_prop"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    
    expr = stmt.expression
    assert isinstance(expr, ast.MemberAccessExpression)
    _check_identifier(expr.object, "my_obj")
    _check_identifier(expr.property, "my_prop")

    assert expr.token_literal() == "."
    assert str(expr) == "(my_obj.my_prop)"

def test_assignment_expression_str():
    """Covers the __str__ method of AssignmentExpression."""
    source_code = "x = 5"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert str(program) == "(x = 5)"

def test_continue_statement_with_value():
    """Covers the token_literal for ContinueStatement."""
    source_code = "con 1"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ContinueStatement)
    # This call covers ContinueStatement.token_literal
    assert stmt.token_literal() == "con"

# In tests/test_parser.py

def test_error_handling_and_recovery():
    """
    Covers multiple error-related branches at once by providing code
    with a syntax error, followed by a valid statement.
    """
    # This source code has one error: `if x y` is missing a '{'.
    # The parser should report this error, then recover by synchronizing
    # to the next valid statement starter (`ret`), and parse it correctly.
    source_code = "if x y\nret 10"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    # Assert that exactly one error was found.
    assert len(parser.errors) == 1, "Expected exactly one parsing error."
    
    # Assert that the parser recovered and parsed the final valid statement.
    assert len(program.statements) == 1, "Parser should recover and parse one valid statement."
    assert isinstance(program.statements[0], ast.ReturnStatement)
    
    # Check the specific error message.
    assert "Expected '{' after if condition" in str(parser.errors[0])



def test_parse_statement_on_none_token():
    """
    Covers the `if self.current_token is None:` branch in `parse_statement`.
    This requires manually setting the parser to an invalid state.
    """
    lexer = Lexer("") # Empty input
    parser = create_parser(lexer)
    
    # Manually set the token to None to simulate the edge case.
    parser.current_token = None
    
    # The method should gracefully return None.
    assert parser.parse_statement() is None


def test_no_prefix_parselet_error():
    """
    Covers the `if prefix_parselet is None:` branch in `parse_expression`.
    """
    # The '}' token has no registered prefix parselet.
    source_code = "}"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    parser.parse_program()

    assert len(parser.errors) == 1
    assert "Unexpected token '}'" in str(parser.errors[0])

def test_def_statement_empty_fields():
    """Covers the empty field list branch in _parse_field_list."""
    source_code = "def {} EmptyStruct"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()

    check_parser_errors(parser)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.DefStatement)
    assert stmt.name.value == "EmptyStruct"
    assert len(stmt.fields) == 0

def test_def_statement_missing_lbrace_error():
    """Covers the error branch for a missing '{' after 'def'."""
    source_code = "def Point"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()

    assert len(parser.errors) == 1
    assert "Expected '{' after 'def' keyword" in str(parser.errors[0])

def test_def_statement_missing_name_error():
    """Covers the error branch for a missing struct name after '}'."""
    source_code = "def { x: i32 }"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()

    assert len(parser.errors) == 1
    assert "Expected an identifier for the struct name after '}'" in str(parser.errors[0])

@pytest.mark.parametrize("source_code, expected_error_msg", [
    ("def { 5: i32 } Point", "Expected an identifier for field name"),
    ("def { x i32 } Point", "Expected ':' after field name 'x'"),
    ("def { x: i32, x: bool } Point", "Duplicate field name 'x'"),
    ("def { x: i32", "Expected '}' to close struct definition"),
])
def test_def_statement_field_errors(source_code: str, expected_error_msg: str):
    """Covers various error conditions within a struct's field list."""
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()

    assert len(parser.errors) == 1
    assert expected_error_msg in str(parser.errors[0])

def test_if_else_missing_lbrace_error():
    """Covers the error branch for an 'else' without a following '{'."""
    source_code = "if true { 1 } else 2"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Expected '{' after 'else' keyword" in str(parser.errors[0])

def test_invalid_assignment_target_error():
    """Covers the error for assigning to an invalid target like a number."""
    source_code = "5 = 6"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Invalid assignment target" in str(parser.errors[0])

def test_function_call_no_arguments():
    """Covers a function call with no arguments."""
    source_code = "my_func()"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert str(program) == "my_func()"

def test_grouped_expression_missing_rparen_error():
    """Covers an unclosed grouped expression."""
    source_code = "(5 + 10"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Expected ')' after expression" in str(parser.errors[0])

def test_block_statement_missing_rbrace_error():
    """Covers an unclosed block statement."""
    source_code = "if true { 1"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Expected '}' to close the block" in str(parser.errors[0])

@pytest.mark.parametrize("source_code, expected_error_msg", [
    ("@ { }", "Expected an identifier for the flow name after '@'"),
    ("@my_flow 123", "Expected '{' after flow name 'my_flow'"),
])
def test_flow_statement_syntax_errors(source_code: str, expected_error_msg: str):
    """Covers syntax errors in a flow statement definition."""
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert expected_error_msg in str(parser.errors[0])

def test_invalid_type_annotation_error():
    """Covers an invalid token being used as a type annotation."""
    source_code = "x: 5"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Unexpected token '5' found when expecting a type" in str(parser.errors[0])

def test_float_literal_expression_():
    """Covers parsing of a FloatLiteral."""
    source_code = "3.14"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert str(program) == "3.14"
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.FloatLiteral)

def test_string_literal_expression_():
    """Covers parsing of a StringLiteral."""
    source_code = '"hello world"'
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert str(program) == '"hello world"'
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.StringLiteral)
    assert stmt.expression.value == "hello world"

@pytest.mark.parametrize("source_code, expected_error_msg", [
    ("my_obj.5", "Expected property name after '.'."),
    ("my_obj.", "Unexpected end of file after '.'."),
])
def test_member_access_errors_(source_code: str, expected_error_msg: str):
    """Covers error conditions for member access expressions."""
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert expected_error_msg in str(parser.errors[0])

from claw.parser.expressions.literal import IntegerLiteralParselet, FloatLiteralParselet
from claw.tokens import Token, TokenType

def test_literal_parselet_error_handling():
    """
    Unit tests the error handling within literal parselets by feeding them
    malformed tokens directly, bypassing the lexer. This covers the
    'except ValueError' blocks.
    """
    # Create a dummy parser instance; its state is not needed for this test.
    parser = create_parser(Lexer(""))

    # Test IntegerLiteralParselet with a bad token
    bad_int_token = Token(TokenType.INTEGER, "12a", 1, 1)
    int_parselet = IntegerLiteralParselet()
    with pytest.raises(ParserError) as excinfo:
        int_parselet.parse(parser, bad_int_token)
    assert "Could not parse '12a' as an integer" in str(excinfo.value)

    # Test FloatLiteralParselet with a bad token
    bad_float_token = Token(TokenType.FLOAT, "3.14.15", 1, 1)
    float_parselet = FloatLiteralParselet()
    with pytest.raises(ParserError) as excinfo:
        float_parselet.parse(parser, bad_float_token)
    assert "Could not parse '3.14.15' as a float" in str(excinfo.value)

def test_float_literal_expression():
    """Covers parsing of a FloatLiteral."""
    source_code = "3.14"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert str(program) == "3.14"
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.FloatLiteral)

def test_string_literal_expression():
    """Covers parsing of a StringLiteral."""
    source_code = '"hello world"'
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program = parser.parse_program()
    check_parser_errors(parser)
    assert str(program) == '"hello world"'
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.StringLiteral)
    assert stmt.expression.value == "hello world"

@pytest.mark.parametrize("source_code, expected_error_msg", [
    ("my_obj.5", "Expected property name after '.'."),
    ("my_obj.", "Unexpected end of file after '.'."),
])
def test_member_access_errors(source_code: str, expected_error_msg: str):
    """Covers error conditions for member access expressions."""
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert expected_error_msg in str(parser.errors[0])

def test_function_call_missing_rparen_error():
    """Covers an unclosed function call argument list."""
    source_code = "my_func(a, b"
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    assert "Expected ')' after arguments" in str(parser.errors[0])

def test_function_call_no_args_missing_rparen_error():
    """
    Covers the specific error case where a function call has no arguments
    and is missing the closing parenthesis. This targets the 'else' branch
    in the error handling of `_parse_argument_list`.
    """
    source_code = "my_func("
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    _ = parser.parse_program()
    assert len(parser.errors) == 1
    # The error should be reported at the '(' token.
    error = parser.errors[0]
    assert "Expected ')' after arguments" in str(error)
    assert error.line == 1
    assert error.column == 9 # The position of ')' that expected
