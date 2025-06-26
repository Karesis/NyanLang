from typing import List, Optional
from ..lexer import Lexer
from ..token import Token, TokenType
from ..ast import Program
from .statement import StatementParser
from .expression import ExpressionParser
from .utils import precedences, Precedence 


class Parser:
    """
    主解析器类，作为协调器。

    它不包含具体的解析逻辑，而是将任务委托给子解析器。
    它管理着共享的状态，例如 token 流、错误列表以及对子解析器的引用。
    """
    cur_token: Token
    peek_token: Token

    def __init__(self, lexer: Lexer):
        # 共享状态
        self.lexer: Lexer = lexer
        self.errors: List[str] = []

        c = self.lexer.next_token()
        p = self.lexer.next_token()

        if c is None or p is None:
            raise TypeError("Lexer failed to provide initial tokens. Cannot initialize Parser.")
        
        self.cur_token = c
        self.peek_token = p

        # 组合子解析器
        # 我们将主 Parser 实例 (self) 传递给子解析器，
        # 以便它们可以访问共享状态 (tokens, errors) 和辅助方法 (next_token)。
        self.statements = StatementParser(self)
        self.expressions = ExpressionParser(self)

    # --- 基础辅助函数 (供所有子解析器使用) ---

    def next_token(self):
        """向前移动 token 指针。"""
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_peek(self, t: TokenType) -> bool:
        """
        断言下一个 token 的类型是否符合预期。
        如果符合，则消耗它并返回 True。
        如果不符合，记录错误并返回 False。
        """
        if self.peek_token and self.peek_token.type == t:
            self.next_token()
            return True
        self.peek_error(t)
        return False

    def peek_error(self, t: TokenType):
        """记录一个关于期望的下一个 token 的错误。"""
        msg = (f"expected next token to be {t.name}, "
               f"got {self.peek_token.type.name if self.peek_token else 'EOF'}")
        self.errors.append(msg)

    def peek_precedence(self) -> Precedence:
        """获取下一个 token 的优先级。"""
        if self.peek_token:
            return precedences.get(self.peek_token.type, Precedence.LOWEST)
        return Precedence.LOWEST

    def cur_precedence(self) -> Precedence:
        """获取当前 token 的优先级。"""
        if self.cur_token:
            return precedences.get(self.cur_token.type, Precedence.LOWEST)
        return Precedence.LOWEST

    # --- 顶层解析入口 ---

    def parse_program(self) -> Program:
        """
        解析整个程序，生成 AST 的根节点。
        这是解析过程的唯一入口点。
        """
        program = Program(statements=[])

        while self.cur_token and self.cur_token.type != TokenType.EOF:
            # 将语句解析任务委托给 StatementParser
            stmt = self.statements.parse_statement()
            if stmt:
                program.statements.append(stmt)
            
            # 在每个语句之后前进 token，这是主循环的职责
            self.next_token()
            
        return program