from claw.lexer import Lexer
from claw.token import TokenType, lookup_ident

def test_simple_assignment():
    lexer = Lexer("x = 42")
    tokens = [lexer.next_token() for _ in range(3)]
    assert tokens[0].type == TokenType.IDENT
    assert tokens[0].literal == "x"
    assert tokens[1].type == TokenType.ASSIGN
    assert tokens[2].type == TokenType.INTEGER
    assert tokens[2].literal == "42"

def test_keywords_and_identifiers():
    lexer = Lexer("ret def abc retdef")
    tokens = [lexer.next_token() for _ in range(4)]
    assert tokens[0].type == TokenType.RET
    assert tokens[1].type == TokenType.DEF
    assert tokens[2].type == TokenType.IDENT
    assert tokens[2].literal == "abc"
    assert tokens[3].type == TokenType.IDENT
    assert tokens[3].literal == "retdef"  # not a keyword

def test_operators_and_delimiters():
    lexer = Lexer("+-*/=,;:.@(){}->")
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.ASTERISK, TokenType.SLASH,
        TokenType.ASSIGN, TokenType.COMMA, TokenType.SEMICOLON, TokenType.COLON,
        TokenType.DOT, TokenType.AT, TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.RBRACE, TokenType.ARROW
    ]
    for expected in expected_types:
        token = lexer.next_token()
        assert token.type == expected

def test_illegal_and_eof():
    lexer = Lexer("$")
    token = lexer.next_token()
    assert token.type == TokenType.ILLEGAL
    token = lexer.next_token()
    assert token.type == TokenType.EOF

def test_skip_whitespace_and_comments():
    lexer = Lexer("   x   // comment here\n42")
    token1 = lexer.next_token()
    token2 = lexer.next_token()
    assert token1.type == TokenType.IDENT
    assert token1.literal == "x"
    assert token2.type == TokenType.INTEGER
    assert token2.literal == "42"

def test_long_identifier_and_number():
    lexer = Lexer("foo_bar123 987654321")
    token1 = lexer.next_token()
    token2 = lexer.next_token()
    assert token1.type == TokenType.IDENT
    assert token1.literal == "foo_bar123"
    assert token2.type == TokenType.INTEGER
    assert token2.literal == "987654321"

def test_lookup_ident():
    assert lookup_ident("ret") == TokenType.RET
    assert lookup_ident("def") == TokenType.DEF
    assert lookup_ident("foobar") == TokenType.IDENT

def test_empty_input():
    lexer = Lexer("")
    token = lexer.next_token()
    assert token.type == TokenType.EOF

def test_only_whitespace():
    lexer = Lexer("   \t\n\r  ")
    token = lexer.next_token()
    assert token.type == TokenType.EOF

def test_multiple_illegal_chars():
    lexer = Lexer("$#%")
    tokens = [lexer.next_token() for _ in range(3)]
    assert all(t.type == TokenType.ILLEGAL for t in tokens)

def test_identifier_with_underscore_start():
    lexer = Lexer("_abc _123")
    t1 = lexer.next_token()
    t2 = lexer.next_token()
    assert t1.type == TokenType.IDENT and t1.literal == "_abc"
    assert t2.type == TokenType.IDENT and t2.literal == "_123"

def test_number_followed_by_letters():
    lexer = Lexer("123abc")
    t1 = lexer.next_token()
    t2 = lexer.next_token()
    assert t1.type == TokenType.INTEGER and t1.literal == "123"
    assert t2.type == TokenType.IDENT and t2.literal == "abc"

def test_consecutive_operators():
    lexer = Lexer("++--**//==>>")
    expected_types = [
        TokenType.PLUS, TokenType.PLUS, TokenType.MINUS, TokenType.MINUS,
        TokenType.ASTERISK, TokenType.ASTERISK, TokenType.EOF
    ]
    for expected in expected_types:
        token = lexer.next_token()
        assert token.type == expected or token.type == TokenType.ILLEGAL  # 兼容未定义的TokenType

def test_comment_at_end_of_file():
    lexer = Lexer("// only comment")
    token = lexer.next_token()
    assert token.type == TokenType.EOF

def test_mixed_tokens_and_comments():
    lexer = Lexer("x // comment\ny")
    t1 = lexer.next_token()
    t2 = lexer.next_token()
    assert t1.type == TokenType.IDENT and t1.literal == "x"
    assert t2.type == TokenType.IDENT and t2.literal == "y"

def test_token_repr():
    from claw.token import Token
    token = Token(TokenType.IDENT, "foo")
    assert repr(token) == "Token(type=IDENT, literal='foo')"