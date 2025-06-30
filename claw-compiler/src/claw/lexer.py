"""
Defines the Lexer for the Claw programming language.

The Lexer's role is to take raw source code as a string and break it down into
a sequence of tokens. It handles identifying keywords, identifiers, literals,
operators, and skipping whitespace and comments, while also tracking the line
and column number for accurate error reporting.
"""

from .tokens import Token, TokenType, check_keyword
from .errors import LexerError


class Lexer:
    """
    A lexical analyzer for the Claw language. It processes an input string
    character by character to produce a stream of tokens.
    """
    def __init__(self, source_code: str) -> None:
        self.source_code: str = source_code
        self.position: int = 0          # Current character index
        self.read_position: int = 0     # Next character index
        self.line: int = 1              # Current line number (for errors)
        self.column: int = 0            # Current column number (for errors)

        self.read_char()  # Prime the lexer by reading the first character

    def ch(self) -> str:
        """Returns the current character being processed."""
        if self.position >= len(self.source_code):
            return '\0'
        return self.source_code[self.position]

    def read_char(self) -> None:
        """
        Reads the next character, advances position pointers, and updates line/column.
        This is the single source of truth for consuming characters.
        """
        if self.ch() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        """Peeks at the next character without consuming it."""
        if self.read_position >= len(self.source_code):
            return '\0'
        return self.source_code[self.read_position]

    def skip_whitespace_and_comments(self) -> None:
        """Skips over any whitespace or single-line comments."""
        while True:
            if self.ch() in (' ', '\t', '\r', '\n'):
                self.read_char()
            # A single-line comment starts with '//'
            elif self.ch() == '/' and self.peek_char() == '/':
                while self.ch() != '\n' and self.ch() != '\0':
                    self.read_char()
            elif self.ch() == '/' and self.peek_char() == '*':
               self.read_char() # Consume '/'
               self.read_char() # Consume '*'
               start_line, start_col = self.line, self.column
               while not (self.ch() == '*' and self.peek_char() == '/'):
                   if self.ch() == '\0':
                       # Optional: More specific error for unterminated multi-line comment
                       raise LexerError("Unterminated multi-line comment", start_line, start_col - 2)
                   self.read_char()
               self.read_char() # Consume '*'
               self.read_char() # Consume '/'
            else:
                break

    def read_identifier(self) -> str:
        """Reads a complete identifier or keyword string."""
        start_pos = self.position
        # Identifiers can contain letters, digits, or '_' (but not start with a digit)
        while self.ch().isalpha() or self.ch().isdigit() or self.ch() == '_':
            self.read_char()
        return self.source_code[start_pos:self.position]

    def read_number(self) -> tuple[TokenType, str]:
        """Reads a complete integer or float literal string."""
        start_pos = self.position
        token_type = TokenType.INTEGER
        while self.ch().isdigit():
            self.read_char()
        
        # Check for a fractional part (making it a float)
        if self.ch() == '.' and self.peek_char().isdigit():
            token_type = TokenType.FLOAT
            self.read_char()  # Consume the '.'
            while self.ch().isdigit():
                self.read_char()
        
        return (token_type, self.source_code[start_pos:self.position])

    def read_string(self) -> str:
        """Reads a complete string literal, handling escape sequences."""
        start_line, start_col = self.line, self.column
        self.read_char()  # Consume the opening '"'

        literal_parts: list[str] = []
        while self.ch() != '"':
            if self.ch() == '\0':
                raise LexerError("Unterminated string", start_line, start_col)

            if self.ch() == '\\': # Escape character
                self.read_char() # Consume the '\'
                if self.ch() == 'n':
                    literal_parts.append('\n')
                elif self.ch() == 't':
                    literal_parts.append('\t')
                elif self.ch() == '"':
                    literal_parts.append('"')
                elif self.ch() == '\\':
                    literal_parts.append('\\')
                else:
                    # Or raise an error for an unsupported escape sequence
                    literal_parts.append('\\' + self.ch())
            else:
                literal_parts.append(self.ch())
            
            self.read_char()
        
        self.read_char()  # Consume the closing '"'
        return "".join(literal_parts)

    def next_token(self) -> Token:
        """Analyzes the input to produce the next token."""
        self.skip_whitespace_and_comments()

        start_line, start_col = self.line, self.column 
        current_char = self.ch()

        tok: Token | None = None

        # Handle simple, single-character tokens
        simple_tokens = {
            '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.ASTERISK,
            '/': TokenType.SLASH, '(': TokenType.LPAREN, ')': TokenType.RPAREN,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE, ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON, '.': TokenType.DOT, '@': TokenType.AT,
            '~': TokenType.TILDE, '\0': TokenType.EOF
        }

        # Handle two-character and compound tokens first
        if current_char == '=':
            if self.peek_char() == '=':
                self.read_char() # consume '='
                tok = Token(TokenType.EQUALS, "==", start_line, start_col)
            else:
                tok = Token(TokenType.ASSIGN, "=", start_line, start_col)
        elif current_char == '!':
            if self.peek_char() == '=':
                self.read_char() # consume '!'
                tok = Token(TokenType.NOT_EQUALS, "!=", start_line, start_col)
        elif current_char == '<':
            if self.peek_char() == '=':
                self.read_char() # consume '<'
                tok = Token(TokenType.LTE, "<=", start_line, start_col)
            else:
                tok = Token(TokenType.LT, "<", start_line, start_col)
        elif current_char == '>':
            if self.peek_char() == '=':
                self.read_char() # consume '>'
                tok = Token(TokenType.GTE, ">=", start_line, start_col)
            else:
                tok = Token(TokenType.GT, ">", start_line, start_col)
        elif current_char == ':':
            if self.peek_char() == '=':
                self.read_char() # consume ':'
                tok = Token(TokenType.COLON_ASSIGN, ":=", start_line, start_col)
            else:
                tok = Token(TokenType.COLON, ":", start_line, start_col)
        elif current_char in simple_tokens:
             # Handle -> separately since '-' is also a standalone operator
            if current_char == '-' and self.peek_char() == '>':
                self.read_char() # consume '-'
                tok = Token(TokenType.ARROW, "->", start_line, start_col)
            else:
                tok = Token(simple_tokens[current_char], current_char, start_line, start_col)

        if tok:
            self.read_char() # Consume the last character of the token
            return tok

        # Handle multi-character literals: identifiers, numbers, strings
        if self.ch().isalpha() or self.ch() == '_':
            literal = self.read_identifier()
            token_type = check_keyword(literal)
            return Token(token_type, literal, start_line, start_col)
        elif self.ch().isdigit():
            token_type, literal = self.read_number()
            return Token(token_type, literal, start_line, start_col)
        elif self.ch() == '"':
            literal = self.read_string()
            return Token(TokenType.STRING, literal, start_line, start_col)

        # If we reach here, the character is not supported
        unrecognized_char = self.ch()
        self.read_char() # Move past the bad character
        raise LexerError(f"Unrecognized character: '{unrecognized_char}'", start_line, start_col)