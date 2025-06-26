# src/claw/parser/expression_parser.py
"""
此模块定义了 ExpressionParser，负责解析所有类型的表达式。
它包含了 Pratt 解析器的核心实现。
"""
from typing import Optional, Callable, List

from ..token import TokenType
from ..ast import (
    Expression, IntegerLiteral, PrefixExpression, InfixExpression, Identifier,
    CallExpression, StructLiteral, MemberAccessExpression, AssignmentExpression
)
from .utils import Precedence

# 为了类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import Parser

# 类型别名，用于定义分派表
PrefixParseFn = Callable[[], Optional[Expression]]
InfixParseFn = Callable[[Expression], Optional[Expression]]


class ExpressionParser:
    def __init__(self, parser: 'Parser'):
        # 持有主 Parser 的引用
        self.p = parser
        
        # Pratt 解析器的核心：分派表
        self.prefix_parse_fns: dict[TokenType, PrefixParseFn] = {}
        self.infix_parse_fns: dict[TokenType, InfixParseFn] = {}
        
        # 注册所有前缀和中缀处理函数
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INTEGER, self.parse_integer_literal)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACE, self.parse_struct_literal)
        self.register_infix(TokenType.DOT, self.parse_member_access_expression)
        self.register_infix(TokenType.ASSIGN, self.parse_assignment_expression)

    def register_prefix(self, tt: TokenType, fn: PrefixParseFn):
        self.prefix_parse_fns[tt] = fn

    def register_infix(self, tt: TokenType, fn: InfixParseFn):
        self.infix_parse_fns[tt] = fn
        
    def parse_expression(self, precedence: Precedence) -> Optional[Expression]:
        """ Pratt 解析器的核心驱动函数 """
        if self.p.cur_token is None:
            return None
        
        prefix = self.prefix_parse_fns.get(self.p.cur_token.type)
        if not prefix:
            self.p.errors.append(f"no prefix parse function for {self.p.cur_token.type.name} found")
            return None
        
        left_exp = prefix()

        while (self.p.peek_token and 
               self.p.peek_token.type != TokenType.SEMICOLON and 
               precedence < self.p.peek_precedence()):
            
            infix = self.infix_parse_fns.get(self.p.peek_token.type)
            if not infix:
                return left_exp
            
            self.p.next_token()
            left_exp = infix(left_exp)
            
        return left_exp

    # --- Prefix-parsing functions ---

    def parse_identifier(self) -> Identifier:
        return Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)

    def parse_integer_literal(self) -> Optional[IntegerLiteral]:
        try:
            value = int(self.p.cur_token.literal)
            return IntegerLiteral(token=self.p.cur_token, value=value)
        except (ValueError, TypeError):
            msg = f"could not parse {getattr(self.p.cur_token, 'literal', 'None')} as integer"
            self.p.errors.append(msg)
            return None

    def parse_prefix_expression(self) -> PrefixExpression:
        token = self.p.cur_token
        self.p.next_token()
        right = self.parse_expression(Precedence.PREFIX)
        return PrefixExpression(token=token, operator=token.literal, right=right)

    def parse_grouped_expression(self) -> Optional[Expression]:
        self.p.next_token()
        exp = self.parse_expression(Precedence.LOWEST)
        if not self.p.expect_peek(TokenType.RPAREN):
            return None
        return exp

    # --- Infix-parsing functions ---

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        token = self.p.cur_token
        precedence = self.p.cur_precedence()
        self.p.next_token()
        right = self.parse_expression(precedence)
        return InfixExpression(token=token, left=left, operator=token.literal, right=right)

    def parse_call_expression(self, function: Expression) -> CallExpression:
        arguments = self.parse_call_arguments()
        return CallExpression(token=self.p.cur_token, function=function, arguments=arguments)

    def parse_call_arguments(self) -> Optional[List[Expression]]:
        args = []
        if self.p.peek_token.type == TokenType.RPAREN:
            self.p.next_token()
            return args

        self.p.next_token()
        args.append(self.parse_expression(Precedence.LOWEST))

        while self.p.peek_token.type == TokenType.COMMA:
            self.p.next_token()
            self.p.next_token()
            args.append(self.parse_expression(Precedence.LOWEST))

        if not self.p.expect_peek(TokenType.RPAREN):
            return None
        return args

    def parse_assignment_expression(self, left: Expression) -> Optional[Expression]:
        if not isinstance(left, (Identifier, MemberAccessExpression)):
            self.p.errors.append("Invalid assignment target")
            return None
        
        token = self.p.cur_token
        precedence = self.p.cur_precedence()
        self.p.next_token()
        value = self.parse_expression(precedence)
        
        return AssignmentExpression(token=token, left=left, value=value)

    def parse_member_access_expression(self, left: Expression) -> Optional[Expression]:
        token = self.p.cur_token # '.' token
        if not self.p.expect_peek(TokenType.IDENT):
            return None
        field = Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)
        return MemberAccessExpression(token=token, object=left, field=field)

    def parse_struct_literal(self, type_name: Expression) -> Optional[StructLiteral]:
        literal_token = self.p.cur_token # '{'
        if not isinstance(type_name, Identifier):
            self.p.errors.append("Expected a struct name before '{'")
            return None
        
        members = []
        if self.p.peek_token.type == TokenType.RBRACE:
            self.p.next_token()
            return StructLiteral(token=literal_token, type_name=type_name, members=members)
        
        self.p.next_token() # 消耗第一个成员名
        while True:
            if self.p.cur_token.type != TokenType.IDENT:
                self.p.errors.append("Expected member name"); return None
            ident = Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)
            
            if not self.p.expect_peek(TokenType.COLON): return None
            self.p.next_token() # 消耗 ':'
            
            value = self.parse_expression(Precedence.LOWEST)
            members.append((ident, value))
            
            if self.p.peek_token.type == TokenType.RBRACE:
                break
            if not self.p.expect_peek(TokenType.COMMA): return None
            self.p.next_token() # 消耗 ','
            
        if not self.p.expect_peek(TokenType.RBRACE): return None
        return StructLiteral(token=literal_token, type_name=type_name, members=members)