from claw.tokens import Token, TokenType
from claw import ast

# =============================================================================
# Foundational Tests
# =============================================================================

def test_identifier_creation_and_literal():
    """
    Tests the creation of a simple Identifier node and its token_literal method.
    """
    token = Token(TokenType.IDENTIFIER, "my_var", 1, 1)
    ident = ast.Identifier(token=token, value="my_var")

    assert ident.value == "my_var"
    assert ident.token_literal() == "my_var"


def test_let_statement_structure():
    """
    Tests the structure of a LetStatement node.
    Simulates: `my_var: i32 := 5`
    """
    name_token = Token(TokenType.IDENTIFIER, "my_var", 1, 1)
    name_ident = ast.Identifier(token=name_token, value="my_var")

    type_token = Token(TokenType.IDENTIFIER, "i32", 1, 9)
    val_type = ast.SimpleType(token=type_token)

    value_token = Token(TokenType.INTEGER, "5", 1, 16)
    val_expr = ast.IntegerLiteral(token=value_token, value=5)

    let_stmt = ast.LetStatement(
        token=name_token,
        name=name_ident,
        value_type=val_type,
        value=val_expr
    )

    assert let_stmt.token_literal() == "my_var"
    assert isinstance(let_stmt.name, ast.Identifier)
    assert let_stmt.name.value == "my_var"
    assert isinstance(let_stmt.value_type, ast.SimpleType)
    assert let_stmt.value_type.token_literal() == "i32"
    assert isinstance(let_stmt.value, ast.IntegerLiteral)
    assert let_stmt.value.value == 5


def test_return_statement_structure():
    """
    Tests the structure of a ReturnStatement node.
    Simulates: `ret 10`
    """
    ret_token = Token(TokenType.RET, "ret", 1, 1)
    value_token = Token(TokenType.INTEGER, "10", 1, 5)
    val_expr = ast.IntegerLiteral(token=value_token, value=10)

    ret_stmt = ast.ReturnStatement(token=ret_token, return_value=val_expr)

    assert ret_stmt.token_literal() == "ret"
    assert isinstance(ret_stmt.return_value, ast.IntegerLiteral)
    assert ret_stmt.return_value.value == 10


# =============================================================================
# Expression Tests
# =============================================================================

def test_infix_expression_structure():
    """
    Tests the structure of an InfixExpression node.
    Simulates: `5 + 10`
    """
    plus_token = Token(TokenType.PLUS, "+", 1, 3)
    left_expr = ast.IntegerLiteral(
        token=Token(TokenType.INTEGER, "5", 1, 1), value=5
    )
    right_expr = ast.IntegerLiteral(
        token=Token(TokenType.INTEGER, "10", 1, 5), value=10
    )

    infix_expr = ast.InfixExpression(
        token=plus_token,
        left=left_expr,
        operator="+",
        right=right_expr
    )

    assert infix_expr.token_literal() == "+"
    assert infix_expr.operator == "+"
    assert isinstance(infix_expr.left, ast.IntegerLiteral)
    assert infix_expr.left.value == 5
    assert isinstance(infix_expr.right, ast.IntegerLiteral)
    assert infix_expr.right.value == 10


def test_if_expression_structure():
    """
    Tests the structure of an IfExpression node with an alternative.
    Simulates: `if x { 1 } else { 2 }`
    """
    if_token = Token(TokenType.IF, "if", 1, 1)

    # Condition
    cond_ident = ast.Identifier(
        token=Token(TokenType.IDENTIFIER, "x", 1, 4), value="x"
    )

    # Consequence Block
    cons_expr_stmt = ast.ExpressionStatement(
        expression=ast.IntegerLiteral(
            token=Token(TokenType.INTEGER, "1", 1, 8), value=1
        )
    )
    cons_block = ast.BlockStatement(
        token=Token(TokenType.LBRACE, "{", 1, 6),
        statements=[cons_expr_stmt]
    )

    # Alternative Block
    alt_expr_stmt = ast.ExpressionStatement(
        expression=ast.IntegerLiteral(
            token=Token(TokenType.INTEGER, "2", 1, 18), value=2
        )
    )
    alt_block = ast.BlockStatement(
        token=Token(TokenType.LBRACE, "{", 1, 16),
        statements=[alt_expr_stmt]
    )

    if_expr = ast.IfExpression(
        token=if_token,
        condition=cond_ident,
        consequence=cons_block,
        alternative=alt_block,
    )

    assert if_expr.token_literal() == "if"
    assert isinstance(if_expr.condition, ast.Identifier)
    assert if_expr.condition.value == "x"
    assert len(if_expr.consequence.statements) == 1
    
    consequence_stmt = if_expr.consequence.statements[0]
    
    # 1. Assert it's an ExpressionStatement to safely access .expression
    assert isinstance(consequence_stmt, ast.ExpressionStatement)
    
    # 2. Assert the expression is an IntegerLiteral to safely access .value
    assert isinstance(consequence_stmt.expression, ast.IntegerLiteral)
    assert consequence_stmt.expression.value == 1

    assert if_expr.alternative is not None
    assert len(if_expr.alternative.statements) == 1
    
    # Get the first statement from the alternative block
    alternative_stmt = if_expr.alternative.statements[0]

    # 1. Assert its specific type
    assert isinstance(alternative_stmt, ast.ExpressionStatement)

    # 2. Assert the inner expression's specific type
    assert isinstance(alternative_stmt.expression, ast.IntegerLiteral)
    assert alternative_stmt.expression.value == 2


# =============================================================================
# Complex Literal Tests
# =============================================================================

def test_function_literal_structure():
    """
    Tests the complex structure of a FunctionLiteral node.
    Simulates: `my_func(a: i32) -> bool { ret true }`
    """
    func_token = Token(TokenType.LPAREN, "(", 1, 8) # Token is '('

    # Name
    func_name = ast.Identifier(
        token=Token(TokenType.IDENTIFIER, "my_func", 1, 1), value="my_func"
    )
    
    # Parameters
    param_ident = ast.Identifier(
        token=Token(TokenType.IDENTIFIER, "a", 1, 9), value="a"
    )
    param_type = ast.SimpleType(
        token=Token(TokenType.IDENTIFIER, "i32", 1, 12)
    )

    # Return Type
    return_type = ast.SimpleType(
        token=Token(TokenType.IDENTIFIER, "bool", 1, 21)
    )

    # Body
    ret_stmt = ast.ReturnStatement(
        token=Token(TokenType.RET, "ret", 1, 28),
        return_value=ast.BooleanLiteral(
            token=Token(TokenType.TRUE, "true", 1, 32), value=True
        )
    )
    body_block = ast.BlockStatement(
        token=Token(TokenType.LBRACE, "{", 1, 26), statements=[ret_stmt]
    )

    func_literal = ast.FunctionLiteral(
        token=func_token,
        name=func_name,
        parameters=[param_ident],
        param_types={param_ident: param_type},
        return_type=return_type,
        body=body_block
    )

    assert func_literal.token_literal() == "("
    assert isinstance(func_literal.name, ast.Identifier)
    assert func_literal.name.value == "my_func"
    assert len(func_literal.parameters) == 1
    assert func_literal.parameters[0].value == "a"
    assert func_literal.param_types[param_ident].token_literal() == "i32"
    assert isinstance(func_literal.return_type, ast.SimpleType)
    assert func_literal.return_type.token_literal() == "bool"
    assert len(func_literal.body.statements) == 1
    assert isinstance(func_literal.body.statements[0], ast.ReturnStatement)