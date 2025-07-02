from claw.tokens import Token, TokenType
from claw import ast
import pytest

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
        mutable=False,  # Assuming the variable is immutable
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

# In tests/test_ast.py, add these new test functions at the end of the file.

def test_program_with_no_statements():
    """
    Covers the edge case for Program.token_literal when there are no statements.
    """
    program = ast.Program(statements=[])
    assert program.token_literal() == ""
    assert str(program) == ""

def test_if_expression_without_else_str():
    """
    Covers the __str__ representation of an IfExpression without an 'else' block.
    """
    if_token = Token(TokenType.IF, "if", 1, 1)
    condition = ast.Identifier(
        token=Token(TokenType.IDENTIFIER, "x", 1, 4), value="x"
    )
    consequence = ast.BlockStatement(
        token=Token(TokenType.LBRACE, "{", 1, 6),
        statements=[]
    )
    
    if_expr = ast.IfExpression(
        token=if_token,
        condition=condition,
        consequence=consequence,
        alternative=None # No else block
    )
    
    assert str(if_expr) == "if x {  }"
    assert if_expr.token_literal() == "if"

def test_loop_and_while_expressions():
    """
    Covers LoopExpression and WhileExpression nodes, which are not yet parsed.
    """
    # Loop
    loop_token = Token(TokenType.LOOP, "loop", 1, 1)
    body = ast.BlockStatement(token=Token(TokenType.LBRACE, "{", 1, 6), statements=[])
    loop_expr = ast.LoopExpression(token=loop_token, body=body)
    assert loop_expr.token_literal() == "loop"
    assert str(loop_expr) == "loop {  }"

    # While
    while_token = Token(TokenType.WHILE, "while", 1, 1)
    condition = ast.Identifier(token=Token(TokenType.IDENTIFIER, "cond", 1, 7), value="cond")
    while_expr = ast.WhileExpression(token=while_token, condition=condition, body=body)
    assert while_expr.token_literal() == "while"
    assert str(while_expr) == "while cond {  }"

def test_struct_and_function_literals():
    """
    Covers StructLiteral and FunctionLiteral nodes, which are not yet parsed.
    """
    # Struct Literal
    point_token = Token(TokenType.IDENTIFIER, "Point", 1, 1)
    point_ident = ast.Identifier(token=point_token, value="Point")
    struct_lit = ast.StructLiteral(token=point_token, name=point_ident, fields={})
    assert struct_lit.token_literal() == "Point"
    assert str(struct_lit) == "Point{}"

    # Function Literal (a complex case)
    func_token = Token(TokenType.LPAREN, "(", 1, 4)
    add_ident = ast.Identifier(token=Token(TokenType.IDENTIFIER, "add", 1, 1), value="add")
    param_x = ast.Identifier(token=Token(TokenType.IDENTIFIER, "x", 1, 5), value="x")
    param_type = ast.SimpleType(token=Token(TokenType.IDENTIFIER, "i32", 1, 8))
    
    func_lit = ast.FunctionLiteral(
        token=func_token,
        name=add_ident,
        parameters=[param_x],
        param_types={param_x: param_type},
        return_type=None,
        body=ast.BlockStatement(token=Token(TokenType.LBRACE, "{", 1, 12), statements=[])
    )
    assert func_lit.token_literal() == "("
    assert str(func_lit) == "add(x: i32) {  }"

def test_remaining_token_literals():
    """
    Directly tests the `token_literal` methods missed by parser tests.
    """
    # Create dummy tokens and nodes
    float_lit = ast.FloatLiteral(token=Token(TokenType.FLOAT, "1.5", 1, 1), value=1.5)
    string_lit = ast.StringLiteral(token=Token(TokenType.STRING, "hi", 1, 1), value="hi")
    assign_expr = ast.AssignmentExpression(
        token=Token(TokenType.ASSIGN, "=", 1, 1), name=ast.Identifier(token=Token(TokenType.IDENTIFIER, "a", 1, 1), value="a"), value=float_lit
    )
    def_stmt = ast.DefStatement(
        token=Token(TokenType.DEF, "def", 1, 1), name=ast.Identifier(token=Token(TokenType.IDENTIFIER, "T", 1, 1), value="T"), fields={}
    )

    # Assert their token literals
    assert float_lit.token_literal() == "1.5"
    
    # token_literal() should return the raw token content, without quotes.
    assert string_lit.token_literal() == "hi"
    # We can also test __str__ separately to ensure it *does* have quotes.
    assert str(string_lit) == '"hi"'
    
    assert assign_expr.token_literal() == "="
    assert def_stmt.token_literal() == "def"

def test_node_base_class_not_implemented_error():
    """
    Covers the `raise NotImplementedError` in the base Node class.
    
    This test works by creating a valid, concrete subclass of `ast.Node`
    that explicitly calls the base class's `token_literal` method via `super()`.
    This is the correct way to test that a base class method intentionally
    raises this specific error, as opposed to a `TypeError` which would be
    raised if we tried to instantiate an incomplete abstract class.
    """
    class ConcreteButErroneousNode(ast.Node):
        def token_literal(self) -> str:
            # Explicitly call the super-class method to trigger the error.
            return super().token_literal() # type: ignore

    node = ConcreteButErroneousNode()
    with pytest.raises(NotImplementedError):
        node.token_literal()

def test_expression_statement_token_property():
    """
    Covers the `token` property of ExpressionStatement.
    """
    # Create a simple identifier expression
    ident = ast.Identifier(token=Token(TokenType.IDENTIFIER, "a", 1, 1), value="a")
    
    # Wrap it in an ExpressionStatement
    stmt = ast.ExpressionStatement(expression=ident)
    
    # Assert that the statement's token is correctly derived from the expression
    assert stmt.token.literal == "a"

def test_remaining_ast_node_coverage():
    """
    Covers the remaining untested methods and branches in ast.py through
    direct instantiation and assertion.
    """
    # Dummy tokens for constructing nodes
    t_tilde = Token(TokenType.TILDE, "~", 1, 1)
    t_lcurly = Token(TokenType.LBRACE, "{", 1, 1)
    t_ident_i32 = Token(TokenType.IDENTIFIER, "i32", 1, 1)
    t_break = Token(TokenType.BREAK, "break", 1, 1)

    # --- Cover TypeNodes ---
    simple_type = ast.SimpleType(token=t_ident_i32)
    
    # Covers MutableType.token_literal
    mutable_type = ast.MutableType(token=t_tilde, base_type=simple_type)
    assert mutable_type.token_literal() == "~"

    # Covers StructTypeLiteral's methods
    struct_type = ast.StructTypeLiteral(token=t_lcurly, fields={})
    assert struct_type.token_literal() == "{"
    assert str(struct_type) == "{  }"

    # Covers CompositeType's methods
    composite_type = ast.CompositeType(token=t_ident_i32, primary_type=simple_type, struct_type=struct_type)
    assert composite_type.token_literal() == "i32"
    assert str(composite_type) == "i32{  }"

    # --- Cover Literal __str__ ---
    # Covers FloatLiteral.__str__
    float_lit = ast.FloatLiteral(token=Token(TokenType.FLOAT, "3.14", 1, 1), value=3.14)
    assert str(float_lit) == "3.14"

    # Covers BooleanLiteral.__str__
    bool_lit = ast.BooleanLiteral(token=Token(TokenType.TRUE, "true", 1, 1), value=True)
    assert str(bool_lit) == "true"
    
    # --- Cover Statement token_literals ---
    # Covers BlockStatement.token_literal
    block_stmt = ast.BlockStatement(token=t_lcurly, statements=[])
    assert block_stmt.token_literal() == "{"

    # Covers BreakStatement.token_literal
    break_stmt = ast.BreakStatement(token=t_break, return_value=None)
    assert break_stmt.token_literal() == "break"

    # --- Cover Program.token_literal's true branch ---
    program = ast.Program(statements=[break_stmt])
    assert program.token_literal() == "break"
