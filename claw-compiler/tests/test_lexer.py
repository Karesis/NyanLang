from claw.lexer import Lexer
from claw.tokens import TokenType, Token
from claw.errors import LexerError
import pytest

def test_single_plus_token():
    """
    test the lexer can correctly parse a single plus token '+'.
    This is the simplest "smoke test" to ensure the basic flow works.
    """
    # 1. Arrange: Define the source code to be tested
    source_code = "+"

    # 2. Act: Create a Lexer instance and get the next token
    lexer = Lexer(source_code)
    token = lexer.next_token()

    # 3. Assert: Verify the result is as expected
    # We expect to get a Token of type PLUS with literal value "+"
    assert token.token_type == TokenType.PLUS
    assert token.literal == "+"
    assert token.line == 1
    assert token.column == 1

    # We also expect an EOF token after the "+"
    eof_token = lexer.next_token()
    assert eof_token.token_type == TokenType.EOF

def test_simple_assignment_sequence():
    """
    Test a complete sequence containing variable definition, assignment, and integer.
    """
    source_code = "age: i32 := 25;"

    # 1. Arrange: Define the expected Token sequence
    expected_tokens = [
        Token(TokenType.IDENTIFIER, "age", 1, 1),
        Token(TokenType.COLON, ":", 1, 4),
        Token(TokenType.IDENTIFIER, "i32", 1, 6),
        Token(TokenType.COLON_ASSIGN, ":=", 1, 10),
        Token(TokenType.INTEGER, "25", 1, 13),
        Token(TokenType.SEMICOLON, ";", 1, 15),
        Token(TokenType.EOF, '\0', 1, 16), # 注意 EOF 的位置
    ]

    # 2. Act:
    lexer = Lexer(source_code)

    # 3. Assert: Verify each generated Token against the expected sequence
    for expected_token in expected_tokens:
        token = lexer.next_token()
        print(f"Generated: {token}, Expected: {expected_token}") # 调试时很有用
        assert token.token_type == expected_token.token_type
        assert token.literal == expected_token.literal
        # 注意：这里的 line/column 检查非常重要，能确保位置追踪是准确的
        assert token.line == expected_token.line
        assert token.column == expected_token.column

# 使用 parametrize 装饰器
@pytest.mark.parametrize("source_code, expected_tokens", [
    # 测试用例 1: 简单的赋值
    ("x := 5", [
        Token(TokenType.IDENTIFIER, "x", 1, 1),
        Token(TokenType.COLON_ASSIGN, ":=", 1, 3),
        Token(TokenType.INTEGER, "5", 1, 6),
        Token(TokenType.EOF, '\0', 1, 7),
    ]),
    
    # 测试用例 2: 函数定义
    ("add(x: i32) -> i32", [
        Token(TokenType.IDENTIFIER, "add", 1, 1),
        Token(TokenType.LPAREN, "(", 1, 4),
        Token(TokenType.IDENTIFIER, "x", 1, 5),
        Token(TokenType.COLON, ":", 1, 6),
        Token(TokenType.IDENTIFIER, "i32", 1, 8),
        Token(TokenType.RPAREN, ")", 1, 11),
        Token(TokenType.ARROW, "->", 1, 13),
        Token(TokenType.IDENTIFIER, "i32", 1, 16),
        Token(TokenType.EOF, '\0', 1, 19),
    ]),

    # 测试用例 3: 包含所有简单符号
    ("= + - * / () {},;.~@", [
        Token(TokenType.ASSIGN, "=", 1, 1),
        Token(TokenType.PLUS, "+", 1, 3),
        Token(TokenType.MINUS, "-", 1, 5),
        Token(TokenType.ASTERISK, "*", 1, 7),
        Token(TokenType.SLASH, "/", 1, 9),
        Token(TokenType.LPAREN, "(", 1, 11),
        Token(TokenType.RPAREN, ")", 1, 12),
        Token(TokenType.LBRACE, "{", 1, 14),
        Token(TokenType.RBRACE, "}", 1, 15),
        Token(TokenType.COMMA, ",", 1, 16),
        Token(TokenType.SEMICOLON, ";", 1, 17),
        Token(TokenType.DOT, ".", 1, 18),
        Token(TokenType.TILDE, "~", 1, 19),
        Token(TokenType.AT, "@", 1, 20),
        Token(TokenType.EOF, '\0', 1, 21),
    ]),

    # 测试用例 4: 测试 peek_char 在文件末尾的行为
    ("x :", [
    Token(TokenType.IDENTIFIER, "x", 1, 1),
    Token(TokenType.COLON, ":", 1, 3),
    Token(TokenType.EOF, '\0', 1, 4),
    ]),

    # 测试用例 5: 测试浮点数
    ("pi := 3.14;", [
    Token(TokenType.IDENTIFIER, "pi", 1, 1),
    Token(TokenType.COLON_ASSIGN, ":=", 1, 4),
    Token(TokenType.FLOAT, "3.14", 1, 7),
    Token(TokenType.SEMICOLON, ";", 1, 11),
    Token(TokenType.EOF, '\0', 1, 12),
    ]),

    # 测试用例 6: 测试包含所有转义字符的字符串
    # 源字符串: "a\n\t\"\\?b"
    # Python 表示: '"a\\n\\t\\"\\\\?b"'
    # Lexer 解析后的字面值: 'a\n\t"\\?b'
    ('"a\\n\\t\\"\\\\?b"', [
    Token(TokenType.STRING, 'a\n\t"\\?b', 1, 1),
    Token(TokenType.EOF, '\0', 1, 14),
    ]),

    # 测试用例 7：测试所有未覆盖的复合操作符和字符串
    ("== != <= >= \"a string\"", [
        Token(TokenType.EQUALS, "==", 1, 1),
        Token(TokenType.NOT_EQUALS, "!=", 1, 4),
        Token(TokenType.LTE, "<=", 1, 7),
        Token(TokenType.GTE, ">=", 1, 10),
        Token(TokenType.STRING, "a string", 1, 13),
        Token(TokenType.EOF, '\0', 1, 23),
    ]),

    # 测试用例 8：同时测试 peek_char 末尾问题和 < > 单独操作符问题
    ("a < b >", [
        Token(TokenType.IDENTIFIER, "a", 1, 1),
        Token(TokenType.LT, "<", 1, 3),
        Token(TokenType.IDENTIFIER, "b", 1, 5),
        Token(TokenType.GT, ">", 1, 7),
        Token(TokenType.EOF, '\0', 1, 8),
    ]),

    # 测试用例 9：测试不支持的转义序列
    # Nyanlang 源代码是 "a\qb"，在 Python 字符串中表示为 '"a\\qb"'
    ('"a\\qb"', [
        # Lexer 应该把 \q 当作一个字面上的 "\q" 字符串
        Token(TokenType.STRING, 'a\\q' + 'b', 1, 1),
        Token(TokenType.EOF, '\0', 1, 7),
    ]),
        
    # 你可以继续在这里添加任意多的测试用例！
])
def test_various_sequences(source_code: str, expected_tokens: list[Token]):
    """
    使用参数化来测试多种不同的代码序列。
    """
    lexer = Lexer(source_code)
    for expected_token in expected_tokens:
        token = lexer.next_token()
        # 为了简洁，我们可以直接比较整个 token 对象
        # dataclass 的 __eq__ 方法默认会比较所有字段
        assert token == expected_token

def test_lexer_handles_whitespace_and_comments():
    """
    验证词法分析器能正确地跳过各种空格、换行和注释，
    并且正确地更新行列号。
    """
    # 源代码包含了各种“干扰项”
    source_code = """
    // 这是一个变量定义
    x: i32 := 5; /* 这是一个
                   多行注释 */
    
    // 下一个是 Flow
    @main;
    """
    
    expected_tokens = [
        Token(TokenType.IDENTIFIER, "x", 4, 5),
        Token(TokenType.COLON, ":", 4, 6),
        Token(TokenType.IDENTIFIER, "i32", 4, 8),
        Token(TokenType.COLON_ASSIGN, ":=", 4, 12),
        Token(TokenType.INTEGER, "5", 4, 15),
        Token(TokenType.SEMICOLON, ";", 4, 16),
        Token(TokenType.AT, "@", 8, 5),
        Token(TokenType.IDENTIFIER, "main", 8, 6),
        Token(TokenType.SEMICOLON, ";", 8, 10),
        Token(TokenType.EOF, '\0', 9, 5),
    ]

    lexer = Lexer(source_code)
    
    for expected_token in expected_tokens:
        token = lexer.next_token()
        assert token == expected_token

@pytest.mark.parametrize("source_code, expected_message, line, column", [
    # 测试用例 1: 更新期望的 message
    ("let a = #;", "[Line 1, Col 9] Error: Unrecognized character: '#'", 1, 9),
    
    # 测试用例 2: 更新期望的 message
    ('x := "hello', "[Line 1, Col 6] Error: Unterminated string", 1, 6),

    # 测试用例 3: 更新期望的 message
    ("/* start ", "[Line 1, Col 1] Error: Unterminated multi-line comment", 1, 1),
])
def test_lexer_raises_errors(source_code: str, expected_message: str, line: int, column: int):
    """
    验证词法分析器在遇到非法输入时，会抛出正确的 LexerError。
    """
    # pytest.raises 是一个上下文管理器，用来断言某段代码会抛出特定异常
    with pytest.raises(LexerError) as excinfo:
        # 把可能会抛出异常的代码放在 with 块内
        lexer = Lexer(source_code)
        # 消耗掉所有 token 直到遇到错误
        while lexer.next_token().token_type != TokenType.EOF:
            pass

    # `excinfo` 是一个包含了异常信息的对象
    # 我们可以进一步断言异常信息是否符合预期
    assert str(excinfo.value) == expected_message
    assert excinfo.value.line == line
    assert excinfo.value.column == column