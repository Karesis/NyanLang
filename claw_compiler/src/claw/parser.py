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


# src/claw/parser.py (fixed and refactored)

from .token import TokenType, Token
from .lexer import Lexer
from .ast import (
    Program, Statement, LetStatement, Identifier, TypeNode,
    ReturnStatement, ExpressionStatement, Expression, IntegerLiteral, PrefixExpression,
    InfixExpression, CallExpression, FunctionDeclaration, BlockStatement,
    StructDefinition, StructLiteral, MemberAccessExpression, AssignmentExpression
)
from typing import List, Optional, Callable, Tuple
from enum import IntEnum

PrefixParseFn = Callable[[], Optional[Expression]]
InfixParseFn = Callable[[Expression], Optional[Expression]]

class Precedence(IntEnum):
    LOWEST, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL, MEMBER = range(8)

precedences = {
    TokenType.ASSIGN: Precedence.EQUALS,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACE: Precedence.CALL,
    TokenType.DOT: Precedence.MEMBER,
}

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.errors: List[str] = []
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

        self.cur_token: Optional[Token] = None
        self.peek_token: Optional[Token] = None
        self.next_token()
        self.next_token()
    
    # --- 基础辅助函数 ---
    def register_prefix(self, tt, fn): self.prefix_parse_fns[tt] = fn
    def register_infix(self, tt, fn): self.infix_parse_fns[tt] = fn
    def next_token(self): self.cur_token, self.peek_token = self.peek_token, self.lexer.next_token()
    def peek_error(self, t): self.errors.append(f"expected next token to be {t.name}, got {self.peek_token.type.name if self.peek_token else 'EOF'}")
    def peek_precedence(self): return precedences.get(self.peek_token.type, Precedence.LOWEST) if self.peek_token else Precedence.LOWEST
    def cur_precedence(self): return precedences.get(self.cur_token.type, Precedence.LOWEST) if self.cur_token else Precedence.LOWEST
    
    def expect_peek(self, t) -> bool:
        if self.peek_token and self.peek_token.type == t:
            self.next_token()
            return True
        self.peek_error(t)
        return False

    # --- 顶层解析 ---
    def parse_program(self) -> Program:
        program = Program(statements=[])
        while self.cur_token and self.cur_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self) -> Optional[Statement]:
        if not self.cur_token:
            return None
            
        # 使用分派字典来简化判断
        dispatch_map = {
            TokenType.DEF: self.parse_struct_definition,
            TokenType.AT: lambda: self.parse_function_declaration(is_flow=True),
            TokenType.RET: self.parse_return_statement,
        }
        if self.cur_token.type in dispatch_map:
            return dispatch_map[self.cur_token.type]()

        # 对 IDENT 开头的语句进行特殊判断
        if self.cur_token.type == TokenType.IDENT:
            if self.peek_token and self.peek_token.type == TokenType.LPAREN:
                return self.parse_function_declaration(is_flow=False)
            if self.peek_token and self.peek_token.type == TokenType.COLON:
                return self.parse_let_statement()
        
        # 默认作为表达式语句处理
        return self.parse_expression_statement()

    # --- 表达式核心 ---
    def parse_expression(self, precedence) -> Optional[Expression]:
        if self.cur_token is None:
            return None
        
        prefix = self.prefix_parse_fns.get(self.cur_token.type)
        if not prefix:
            self.errors.append(f"no prefix parse func for {self.cur_token.type.name}")
            return None
        
        left_exp = prefix()

        while self.peek_token and self.peek_token.type != TokenType.SEMICOLON and precedence < self.peek_precedence():
            infix = self.infix_parse_fns.get(self.peek_token.type)
            if not infix:
                return left_exp
            
            self.next_token()
            left_exp = infix(left_exp)
            
        return left_exp

    # --- 各种具体的解析函数 ---
    
    def parse_struct_definition(self) -> Optional[StructDefinition]:
        def_token = self.cur_token # 'def'
        
        fields = self.parse_struct_fields()
        if fields is None: return None
        
        if not self.expect_peek(TokenType.IDENT): return None # cur is now struct name
        name = Identifier(token=self.cur_token, value=self.cur_token.literal)
        
        return StructDefinition(token=def_token, name=name, fields=fields)

    def parse_struct_fields(self) -> Optional[List[Tuple[Identifier, TypeNode]]]:
        fields = []
        if not self.expect_peek(TokenType.LBRACE): return None # cur is now '{'
        
        if self.peek_token.type == TokenType.RBRACE:
            self.next_token() # cur is now '}'
            return fields
            
        self.next_token() # cur is now the first field name
        
        while True:
            if self.cur_token.type != TokenType.IDENT:
                self.errors.append("Expected field name"); return None
            ident = Identifier(token=self.cur_token, value=self.cur_token.literal)
            
            if not self.expect_peek(TokenType.COLON): return None # cur is ':'
            if not self.expect_peek(TokenType.IDENT): return None # cur is type
            type_node = TypeNode(token=self.cur_token, name=self.cur_token.literal)
            fields.append((ident, type_node))

            if self.peek_token.type == TokenType.RBRACE:
                break
            if not self.expect_peek(TokenType.COMMA): return None # cur is ','
            self.next_token() # cur is the next field name

        if not self.expect_peek(TokenType.RBRACE): return None # cur is now '}'
        return fields

    def parse_struct_literal(self, type_name: Expression) -> Optional[StructLiteral]:
        literal_token = self.cur_token # '{'
        if not isinstance(type_name, Identifier):
            self.errors.append("Expected a struct name before '{'"); return None
        
        members = []
        if self.peek_token.type == TokenType.RBRACE:
            self.next_token()
            return StructLiteral(token=literal_token, type_name=type_name, members=members)
        
        self.next_token() # cur is first member name
        while True:
            if self.cur_token.type != TokenType.IDENT:
                self.errors.append("Expected member name"); return None
            ident = Identifier(token=self.cur_token, value=self.cur_token.literal)
            
            if not self.expect_peek(TokenType.COLON): return None # cur is ':'
            self.next_token() # cur is start of expression
            
            value = self.parse_expression(Precedence.LOWEST)
            members.append((ident, value))
            
            if self.peek_token.type == TokenType.RBRACE:
                break
            if not self.expect_peek(TokenType.COMMA): return None
            self.next_token() # cur is next member name
            
        if not self.expect_peek(TokenType.RBRACE): return None
        return StructLiteral(token=literal_token, type_name=type_name, members=members)

    def parse_assignment_expression(self, left: Expression) -> Optional[Expression]:
        if not isinstance(left, (Identifier, MemberAccessExpression)):
            self.errors.append("Invalid assignment target")
            return None
        
        token = self.cur_token
        precedence = self.cur_precedence()
        self.next_token()
        value = self.parse_expression(precedence)
        
        return AssignmentExpression(token=token, left=left, value=value)

    def parse_member_access_expression(self, left: Expression) -> Optional[Expression]:
        token = self.cur_token
        if not self.expect_peek(TokenType.IDENT):
            return None
        field = Identifier(token=self.cur_token, value=self.cur_token.literal)
        return MemberAccessExpression(token=token, object=left, field=field)

    def parse_let_statement(self):
        let_token = self.cur_token
        name = Identifier(token=let_token, value=let_token.literal)
        if not self.expect_peek(TokenType.COLON): return None
        self.next_token()
        type_node = TypeNode(token=self.cur_token, name=self.cur_token.literal)
        value = None
        if self.peek_token and self.peek_token.type == TokenType.ASSIGN:
            self.next_token()
            self.next_token()
            value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token and self.peek_token.type == TokenType.SEMICOLON:
            self.next_token()
        return LetStatement(token=let_token, name=name, type=type_node, value=value)

    def parse_expression_statement(self):
        stmt = ExpressionStatement(token=self.cur_token, expression=self.parse_expression(Precedence.LOWEST))
        if self.peek_token and self.peek_token.type == TokenType.SEMICOLON:
            self.next_token()
        return stmt

    def parse_identifier(self):
        return Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self):
        try:
            return IntegerLiteral(token=self.cur_token, value=int(self.cur_token.literal))
        except (ValueError, TypeError):
            self.errors.append(f"could not parse {getattr(self.cur_token, 'literal', 'None')} as int")
            return None

    def parse_prefix_expression(self):
        token = self.cur_token
        self.next_token()
        return PrefixExpression(token=token, operator=token.literal, right=self.parse_expression(Precedence.PREFIX))

    def parse_infix_expression(self, left):
        token = self.cur_token
        precedence = self.cur_precedence()
        self.next_token()
        return InfixExpression(token=token, left=left, operator=token.literal, right=self.parse_expression(precedence))

    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(TokenType.RPAREN):
            return None
        return exp

    def parse_call_expression(self, function):
        return CallExpression(token=self.cur_token, function=function, arguments=self.parse_call_arguments())

    def parse_call_arguments(self):
        args = []
        if self.peek_token.type == TokenType.RPAREN:
            self.next_token()
            return args
        self.next_token()
        args.append(self.parse_expression(Precedence.LOWEST))
        while self.peek_token.type == TokenType.COMMA:
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(Precedence.LOWEST))
        if not self.expect_peek(TokenType.RPAREN):
            return None
        return args

    def parse_function_declaration(self, is_flow):
        if is_flow:
            self.next_token()
        token = self.cur_token
        name = Identifier(token=token, value=token.literal)
        params = []
        if not is_flow:
            if not self.expect_peek(TokenType.LPAREN): return None
            params = self.parse_function_parameters()
        if not self.expect_peek(TokenType.ARROW): return None
        self.next_token()
        return_type = TypeNode(token=self.cur_token, name=self.cur_token.literal)
        capture_fields = []
        if not self.expect_peek(TokenType.LBRACE): return None
        body = self.parse_block_statement()
        return FunctionDeclaration(token=token, name=name, params=params, return_type=return_type, capture_fields=capture_fields, body=body, is_flow=is_flow)

    def parse_function_parameters(self):
        params = []
        if self.peek_token.type == TokenType.RPAREN:
            self.next_token()
            return params
        self.next_token()
        while True:
            ident = Identifier(token=self.cur_token, value=self.cur_token.literal)
            if not self.expect_peek(TokenType.COLON): return None
            self.next_token()
            type_node = TypeNode(token=self.cur_token, name=self.cur_token.literal)
            params.append((ident, type_node))
            if self.peek_token.type == TokenType.RPAREN:
                break
            if not self.expect_peek(TokenType.COMMA):
                return None
            self.next_token()
        if not self.expect_peek(TokenType.RPAREN):
            return None
        return params

    def parse_block_statement(self):
        block_token = self.cur_token
        stmts = []
        self.next_token()
        while self.cur_token and self.cur_token.type != TokenType.RBRACE and self.cur_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            self.next_token()
        return BlockStatement(token=block_token, statements=stmts)

    def parse_return_statement(self):
        stmt = ReturnStatement(token=self.cur_token, return_value=None)
        self.next_token()
        stmt.return_value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token and self.peek_token.type == TokenType.SEMICOLON:
            self.next_token()
        return stmt