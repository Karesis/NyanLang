import pytest
from claw.tokens import Token, TokenType, check_keyword

def test_token_creation():
    token = Token(TokenType.IDENTIFIER, "myVar")
    assert token.token_type == TokenType.IDENTIFIER
    assert token.literal == "myVar"
    assert repr(token) == "Token(type=IDENTIFIER, literal='myVar')"

@pytest.mark.parametrize("input_identifier,expected_type", [
    # Test all known keywords
    ("def", TokenType.DEF),
    ("ret", TokenType.RET),
    ("if", TokenType.IF),
    ("else", TokenType.ELSE),
    ("while", TokenType.WHILE),
    ("loop", TokenType.LOOP),
    ("break", TokenType.BREAK),
    ("continue", TokenType.CONTINUE),
    ("true", TokenType.TRUE),
    ("false", TokenType.FALSE),
    
    # Test the alias for 'continue'
    ("con", TokenType.CONTINUE),
    
    # Test some identifiers that are NOT keywords
    ("my_variable", TokenType.IDENTIFIER),
    ("function", TokenType.IDENTIFIER),
    ("return_value", TokenType.IDENTIFIER),
    ("if_statement", TokenType.IDENTIFIER), # An identifier that contains a keyword
])
def test_check_keyword_function(input_identifier: str, expected_type: TokenType):
    assert check_keyword(input_identifier) == expected_type