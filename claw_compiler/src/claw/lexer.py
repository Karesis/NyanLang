# src/claw/lexer.py

"""
Defines the Lexer for the Nyan programming language.

The Lexer's role is to take raw source code as a string and break it down into
a sequence of tokens. It handles basic lexical analysis, such as identifying
keywords, identifiers, literals, operators, and skipping whitespace and comments.
"""

from .token import Token, TokenType, lookup_ident


class Lexer:
    """
    A lexical analyzer for the Nyan language.

    It processes an input string character by character to produce tokens.

    Attributes:
        source_code (str): The source code string to be tokenized.
        position (int): The current character's position in the source code.
        read_position (int): The position of the next character to be read.
        ch (str): The current character being examined.
    """

    def __init__(self, source_code: str) -> None:
        """
        Initializes the Lexer.

        Args:
            source_code: The source code string to tokenize.
        """
        self.source_code: str = source_code
        self.position: int = 0         # Current character position
        self.read_position: int = 0    # Next character position to read
        self.ch: str = ""              # Current character under examination

        self.read_char()  # Prime the lexer by reading the first character.

    def read_char(self) -> None:
        """
        Reads the next character from the input and advances the position pointers.
        If the end of the input is reached, self.ch is set to '\\0' (NUL).
        """
        if self.read_position >= len(self.source_code):
            self.ch = '\0'  # NUL character signifies End Of File (EOF).
        else:
            self.ch = self.source_code[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        """
        "Peeks" at the next character in the input without consuming it.

        Returns:
            The next character, or '\\0' if at the end of the input.
        """
        if self.read_position >= len(self.source_code):
            return '\0'
        return self.source_code[self.read_position]

    def skip_whitespace(self) -> None:
        """Skips over any whitespace characters (spaces, tabs, newlines)."""
        while self.ch in (' ', '\t', '\n', '\r'):
            self.read_char()

    def skip_comment(self) -> None:
        """Skips a single-line comment (from '//' to the end of the line)."""
        while self.ch != '\n' and self.ch != '\0':
            self.read_char()

    def read_identifier(self) -> str:
        """Reads a complete identifier string."""
        start_pos = self.position
        # An identifier starts with a letter or '_' and can be followed
        # by letters, digits, or '_'.
        while is_letter(self.ch) or self.ch.isdigit():
            self.read_char()
        return self.source_code[start_pos:self.position]

    def read_number(self) -> str:
        """Reads a complete integer literal string."""
        start_pos = self.position
        while self.ch.isdigit():
            self.read_char()
        return self.source_code[start_pos:self.position]

    def next_token(self) -> Token:
        """
        Analyzes the current character to produce the next token.

        This is the main method of the lexer. It dispatches to other methods
        based on the current character and returns the corresponding token.
        """
        self.skip_whitespace()

        tok: Token

        match self.ch:
            case '=':
                tok = Token(TokenType.ASSIGN, self.ch)
            case '+':
                tok = Token(TokenType.PLUS, self.ch)
            case '-':
                if self.peek_char() == '>':
                    # Two-character token: ->
                    ch = self.ch
                    self.read_char()  # Consume '-'
                    literal = ch + self.ch
                    tok = Token(TokenType.ARROW, literal)
                else:
                    tok = Token(TokenType.MINUS, self.ch)
            case '*':
                tok = Token(TokenType.ASTERISK, self.ch)
            case '/':
                if self.peek_char() == '/':
                    # This is a single-line comment.
                    self.read_char()  # Consume the first '/'
                    self.read_char()  # Consume the second '/'
                    self.skip_comment()
                    # After skipping, recursively call next_token to get the
                    # actual next token.
                    return self.next_token()
                else:
                    tok = Token(TokenType.SLASH, self.ch)
            case '(':
                tok = Token(TokenType.LPAREN, self.ch)
            case ')':
                tok = Token(TokenType.RPAREN, self.ch)
            case '{':
                tok = Token(TokenType.LBRACE, self.ch)
            case '}':
                tok = Token(TokenType.RBRACE, self.ch)
            case ',':
                tok = Token(TokenType.COMMA, self.ch)
            case ';':
                tok = Token(TokenType.SEMICOLON, self.ch)
            case ':':
                tok = Token(TokenType.COLON, self.ch)
            case '.':
                tok = Token(TokenType.DOT, self.ch)
            case '@':
                tok = Token(TokenType.AT, self.ch)
            case '\0':
                tok = Token(TokenType.EOF, "")
            case _:
                if is_letter(self.ch):
                    literal = self.read_identifier()
                    token_type = lookup_ident(literal)  # Check if it's a keyword
                    # read_identifier has already advanced the pointers, so we return early.
                    return Token(token_type, literal)
                elif self.ch.isdigit():
                    literal = self.read_number()
                    # read_number has also advanced, so return early.
                    return Token(TokenType.INTEGER, literal)
                else:
                    tok = Token(TokenType.ILLEGAL, self.ch)

        self.read_char()  # Advance pointers for the next token.
        return tok


# --- Helper Functions ---

def is_letter(ch: str) -> bool:
    """Checks if a character is a letter or an underscore."""
    return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'
