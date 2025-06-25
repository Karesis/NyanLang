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

from .token import Token, TokenType, lookup_ident

class Lexer:
    def __init__(self, source_code: str):
        self.input = source_code
        self.position = 0          # 当前正在读取的字符的位置
        self.read_position = 0     # 即将要读取的下一个字符的位置 (超前一个)
        self.ch = ''               # 当前正在检查的字符

        self.read_char() # 初始化 Lexer

    def read_char(self):
        """
        读取输入中的下一个字符，并前移位置指针。
        """
        if self.read_position >= len(self.input):
            self.ch = '\0'  # 使用 NUL 字符表示 EOF 或未读取任何内容
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        """
        “窥视”下一个字符，但保持当前位置不变。
        """
        if self.read_position >= len(self.input):
            return '\0'
        return self.input[self.read_position]

    def skip_whitespace(self):
        """
        跳过所有空白字符 (空格, tab, 换行)。
        """
        while self.ch in (' ', '\t', '\n', '\r'):
            self.read_char()

    def skip_comment(self):
        """
        跳过单行注释，直到行尾。
        """
        while self.ch != '\n' and self.ch != '\0':
            self.read_char()

    def read_identifier(self) -> str:
        """
        读取一个完整的标识符。
        """
        start_pos = self.position
        # 标识符可以包含字母、数字和下划线，但必须以字母或下划线开头
        if is_letter(self.ch):
            while is_letter(self.ch) or self.ch.isdigit():
                self.read_char()
        return self.input[start_pos:self.position]

    def read_number(self) -> str:
        """
        读取一个完整的数字。
        """
        start_pos = self.position
        while self.ch.isdigit():
            self.read_char()
        return self.input[start_pos:self.position]

    def next_token(self) -> Token:
        """
        核心方法：分析当前字符并返回对应的 Token。
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
                    ch = self.ch
                    self.read_char() # 消费 '-'
                    literal = ch + self.ch
                    tok = Token(TokenType.ARROW, literal)
                else:
                    tok = Token(TokenType.MINUS, self.ch)
            case '*':
                tok = Token(TokenType.ASTERISK, self.ch)
            case '/':
                if self.peek_char() == '/':
                    self.read_char() # 消费第一个 '/'
                    self.read_char() # 消费第二个 '/'
                    self.skip_comment()
                    return self.next_token() # 递归调用以获取注释后的下一个token
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
                    token_type = lookup_ident(literal) # 检查是否为关键字
                    # read_identifier 内部已经移动了指针，所以直接返回
                    return Token(token_type, literal)
                elif self.ch.isdigit():
                    literal = self.read_number()
                    # read_number 内部已经移动了指针，所以直接返回
                    return Token(TokenType.INTEGER, literal)
                else:
                    tok = Token(TokenType.ILLEGAL, self.ch)
        
        self.read_char() # 为下一个 token 前进指针
        return tok

# 辅助函数
def is_letter(ch: str) -> bool:
    return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'