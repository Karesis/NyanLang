"""
   Copyright [2025] [杨亦锋]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    # --- Special Types ---
    ILLEGAL = auto()  # Illegal character or sequence
    EOF = auto()      # End of File

    # --- Identifiers + Literals ---
    IDENT = auto()    # add, foobar, x, y, ...
    INTEGER = auto()  # 123, 42

    # --- Operators ---
    ASSIGN = auto()   # =
    PLUS = auto()     # +
    MINUS = auto()    # -
    ASTERISK = auto() # *
    SLASH = auto()    # /

    # --- Delimiters ---
    COMMA = auto()    # ,
    SEMICOLON = auto()# ;
    COLON = auto()    # :
    DOT = auto()      # .
    AT = auto()       # @

    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACE = auto()   # {
    RBRACE = auto()   # }
    
    ARROW = auto()    # ->

    # --- Keywords ---

    RET = auto()      # ret
    DEF = auto()      # def

@dataclass
class Token:
    """
    表示词法分析器从源代码中提取的单个令牌。
    """
    type: TokenType
    literal: str

    def __repr__(self) -> str:
        return f"Token(type={self.type.name}, literal='{self.literal}')"

# 关键字映射
# 用于词法分析器在识别出标识符后，检查它是否是一个关键字。
keywords = {
    "ret": TokenType.RET,
    "def": TokenType.DEF
}

def lookup_ident(ident: str) -> TokenType:
    """
    检查给定的标识符是否为关键字。
    如果是，返回关键字的 TokenType；否则，返回 IDENT。
    """
    return keywords.get(ident, TokenType.IDENT)