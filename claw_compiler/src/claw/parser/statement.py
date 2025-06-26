# src/claw/parser/statement_parser.py
"""
此模块定义了 StatementParser，负责解析所有类型的语句。
"""
from typing import Optional, List, Tuple

# 注意我们从父级目录导入模块
from ..token import TokenType
from ..ast import (
    Statement, LetStatement, ReturnStatement, ExpressionStatement,
    FunctionDeclaration, BlockStatement, StructDefinition,
    Identifier, TypeNode
)
# 导入Precedence是为了在调用表达式解析时使用
from .utils import Precedence 

# 为了类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import Parser


class StatementParser:
    def __init__(self, parser: 'Parser'):
        # 持有主 Parser 的引用，以便访问共享状态和辅助方法
        self.p = parser

    def parse_statement(self) -> Optional[Statement]:
        """
        根据当前 token 类型，分派到相应的语句解析函数。
        这是语句解析的入口。
        """
        if not self.p.cur_token:
            return None
        
        token_type = self.p.cur_token.type

        if token_type == TokenType.DEF:
            return self.parse_struct_definition()
        elif token_type == TokenType.AT:
            return self.parse_function_declaration(is_flow=True)
        elif token_type == TokenType.RET:
            return self.parse_return_statement()
        elif token_type == TokenType.IDENT:
            # 对于 IDENT 开头的语句，需要根据下一个 token 判断
            if self.p.peek_token and self.p.peek_token.type == TokenType.LPAREN:
                return self.parse_function_declaration(is_flow=False)
            if self.p.peek_token and self.p.peek_token.type == TokenType.COLON:
                return self.parse_let_statement()

        # 如果没有匹配到任何特定的语句类型，则默认作为表达式语句处理
        return self.parse_expression_statement()

    def parse_let_statement(self) -> Optional[LetStatement]:
        let_token = self.p.cur_token
        name = Identifier(token=let_token, value=let_token.literal)

        if not self.p.expect_peek(TokenType.COLON): return None
        self.p.next_token() # 消耗类型标识符
        type_node = TypeNode(token=self.p.cur_token, name=self.p.cur_token.literal)

        value = None
        if self.p.peek_token and self.p.peek_token.type == TokenType.ASSIGN:
            self.p.next_token() # 消耗 '='
            self.p.next_token() # 移动到表达式的开头
            # 将表达式的解析工作委托给 ExpressionParser
            value = self.p.expressions.parse_expression(Precedence.LOWEST)

        if self.p.peek_token and self.p.peek_token.type == TokenType.SEMICOLON:
            self.p.next_token()

        return LetStatement(token=let_token, name=name, type=type_node, value=value)

    def parse_return_statement(self) -> Optional[ReturnStatement]:
        stmt = ReturnStatement(token=self.p.cur_token, return_value=None)
        self.p.next_token() # 消耗 'ret'
        
        # 委托表达式解析
        stmt.return_value = self.p.expressions.parse_expression(Precedence.LOWEST)

        if self.p.peek_token and self.p.peek_token.type == TokenType.SEMICOLON:
            self.p.next_token()
            
        return stmt

    def parse_expression_statement(self) -> ExpressionStatement:
        # 委托表达式解析
        expr = self.p.expressions.parse_expression(Precedence.LOWEST)
        stmt = ExpressionStatement(token=self.p.cur_token, expression=expr)

        if self.p.peek_token and self.p.peek_token.type == TokenType.SEMICOLON:
            self.p.next_token()
            
        return stmt
    
    def parse_block_statement(self) -> BlockStatement:
        block_token = self.p.cur_token # '{'
        stmts = []
        self.p.next_token() # 消耗 '{'

        while self.p.cur_token and self.p.cur_token.type != TokenType.RBRACE and self.p.cur_token.type != TokenType.EOF:
            stmt = self.parse_statement() # 递归调用
            if stmt:
                stmts.append(stmt)
            self.p.next_token() # 在循环中前进
        
        return BlockStatement(token=block_token, statements=stmts)

    def parse_function_declaration(self, is_flow: bool) -> Optional[FunctionDeclaration]:
        if is_flow:
            self.p.next_token() # 消耗 '@'

        token = self.p.cur_token # 函数名
        name = Identifier(token=token, value=token.literal)
        params = []

        if not is_flow:
            if not self.p.expect_peek(TokenType.LPAREN): return None
            params = self.parse_function_parameters()
        
        if not self.p.expect_peek(TokenType.ARROW): return None
        self.p.next_token() # 消耗返回类型
        return_type = TypeNode(token=self.p.cur_token, name=self.p.cur_token.literal)
        
        capture_fields = [] # 暂时为空
        if not self.p.expect_peek(TokenType.LBRACE): return None
        
        body = self.parse_block_statement()
        
        return FunctionDeclaration(token=token, name=name, params=params, return_type=return_type, capture_fields=capture_fields, body=body, is_flow=is_flow)

    def parse_function_parameters(self) -> Optional[List[Tuple[Identifier, TypeNode]]]:
        params = []
        if self.p.peek_token.type == TokenType.RPAREN:
            self.p.next_token() # 消耗 ')'
            return params

        self.p.next_token() # 消耗第一个参数名

        while True:
            ident = Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)
            if not self.p.expect_peek(TokenType.COLON): return None
            self.p.next_token() # 消耗类型
            type_node = TypeNode(token=self.p.cur_token, name=self.p.cur_token.literal)
            params.append((ident, type_node))

            if self.p.peek_token.type == TokenType.RPAREN:
                break
            if not self.p.expect_peek(TokenType.COMMA): return None
            self.p.next_token() # 消耗参数名

        if not self.p.expect_peek(TokenType.RPAREN): return None
        return params

    def parse_struct_definition(self) -> Optional[StructDefinition]:
        def_token = self.p.cur_token # 'def'
        
        fields = self.parse_struct_fields()
        if fields is None: return None
        
        if not self.p.expect_peek(TokenType.IDENT): return None # cur is now struct name
        name = Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)
        
        return StructDefinition(token=def_token, name=name, fields=fields)

    def parse_struct_fields(self) -> Optional[List[Tuple[Identifier, TypeNode]]]:
        fields = []
        if not self.p.expect_peek(TokenType.LBRACE): return None # cur is now '{'
        
        if self.p.peek_token.type == TokenType.RBRACE:
            self.p.next_token()
            return fields
            
        self.p.next_token() # 消耗第一个字段名
        
        while True:
            if self.p.cur_token.type != TokenType.IDENT:
                self.p.errors.append("Expected field name"); return None
            ident = Identifier(token=self.p.cur_token, value=self.p.cur_token.literal)
            
            if not self.p.expect_peek(TokenType.COLON): return None
            if not self.p.expect_peek(TokenType.IDENT): return None
            type_node = TypeNode(token=self.p.cur_token, name=self.p.cur_token.literal)
            fields.append((ident, type_node))

            if self.p.peek_token.type == TokenType.RBRACE:
                break
            if not self.p.expect_peek(TokenType.COMMA): return None
            self.p.next_token() # 消耗下一个字段名

        if not self.p.expect_peek(TokenType.RBRACE): return None
        return fields