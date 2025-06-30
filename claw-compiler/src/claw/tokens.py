from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # --- Special Tokens ---
    ILLEGAL = auto()  # An unknown or unsupported token
    EOF = auto()  # End of File

    # --- Delimiters ---
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;
    COLON = auto()  # :
    DOT = auto()  # .

    # --- Operators ---
    ASSIGN = auto()  # =
    PLUS = auto()  # +
    MINUS = auto()  # -
    ASTERISK = auto()  # *
    SLASH = auto()  # /

    # --- Comparison Operators ---
    EQUALS = auto()  # ==
    NOT_EQUALS = auto()  # !=
    LT = auto()  # < (Less Than)
    GT = auto()  # > (Greater Than)
    LTE = auto()  # <= (Less Than or Equal)
    GTE = auto()  # >= (Greater Than or Equal)

    # --- Special Symbols (Nyanlang specific) ---
    ARROW = auto()  # -> (return type arrow)
    AT = auto()  # @  (flow definer)
    TILDE = auto()  # ~  (mutability marker)
    COLON_ASSIGN = auto()  # := (immutable declaration & assignment)

    # --- Literals & Identifiers ---
    IDENTIFIER = auto()  # a, my_var, etc.
    INTEGER = auto()  # 123
    FLOAT = auto()  # 1.23
    STRING = auto()  # "hello"

    # --- Keywords ---
    DEF = auto()  # def
    RET = auto()  # ret
    IF = auto()  # if
    ELSE = auto()  # else
    LOOP = auto()  # loop
    WHILE = auto()  # while
    BREAK = auto()  # break
    CONTINUE = auto()  # continue / con
    TRUE = auto()  # true
    FALSE = auto()  # false


keywords: dict[str, TokenType] = {
    "def": TokenType.DEF,
    "ret": TokenType.RET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "loop": TokenType.LOOP,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "con": TokenType.CONTINUE,  # Alias for continue
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


@dataclass(frozen=True)
class Token:
    """
    Represents a single token extracted from the source code by the lexer.
    It is immutable.
    """

    token_type: TokenType
    literal: str
    line: int
    column: int

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the token."""
        return (f"Token(type={self.token_type.name}, "
                f"literal='{self.literal}', "
                f"line={self.line}, column={self.column})")


def check_keyword(ident: str) -> TokenType:
    """
    Checks if a given identifier string is a keyword.
    """
    return keywords.get(ident, TokenType.IDENTIFIER)
