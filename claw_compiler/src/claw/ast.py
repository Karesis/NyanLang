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

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from .token import Token
from dataclasses import dataclass

# --- 基础接口 ---
class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str: pass
    def __str__(self) -> str: return f"<{self.__class__.__name__}>"

class Statement(Node): pass
class Expression(Node): pass

# --- 根节点 ---
@dataclass
class Program(Node):
    statements: List[Statement]
    def token_literal(self) -> str: return self.statements[0].token_literal() if self.statements else ""

# --- 基础表达式节点 ---
@dataclass
class Identifier(Expression):
    token: Token; value: str
    def token_literal(self) -> str: return self.token.literal
    def __str__(self) -> str: return self.value

@dataclass
class IntegerLiteral(Expression):
    token: Token; value: int
    def token_literal(self) -> str: return self.token.literal
    def __str__(self) -> str: return str(self.value)

# --- 复杂表达式节点 ---
@dataclass
class PrefixExpression(Expression):
    token: Token; operator: str; right: Expression
    def token_literal(self) -> str: return self.token.literal

@dataclass
class InfixExpression(Expression):
    token: Token; left: Expression; operator: str; right: Expression
    def token_literal(self) -> str: return self.token.literal

@dataclass
class CallExpression(Expression):
    token: Token; function: Expression; arguments: List[Expression]
    def token_literal(self) -> str: return self.token.literal

@dataclass
class MemberAccessExpression(Expression):
    token: Token; object: Expression; field: Identifier
    def token_literal(self) -> str: return self.token.literal

@dataclass
class AssignmentExpression(Expression):
    token: Token; left: Expression; value: Expression
    def token_literal(self) -> str: return self.token.literal # [修正] 补上此方法

@dataclass
class StructLiteral(Expression):
    token: Token; type_name: Identifier; members: List[Tuple[Identifier, Expression]]
    def token_literal(self) -> str: return self.token.literal # [修正] 补上此方法

# --- 类型节点 ---
@dataclass
class TypeNode(Node):
    token: Token; name: str
    def token_literal(self) -> str: return self.token.literal
    def __str__(self) -> str: return self.name

# --- 语句节点 ---
@dataclass
class ExpressionStatement(Statement):
    token: Token; expression: Expression
    def token_literal(self) -> str: return self.token.literal

@dataclass
class BlockStatement(Statement):
    token: Token; statements: List[Statement]
    def token_literal(self) -> str: return self.token.literal

@dataclass
class ReturnStatement(Statement):
    token: Token; return_value: Expression
    def token_literal(self) -> str: return self.token.literal

@dataclass
class LetStatement(Statement):
    token: Token; name: Identifier; type: TypeNode; value: Optional[Expression]
    def token_literal(self) -> str: return self.token.literal

# --- 声明节点 ---
@dataclass
class FunctionDeclaration(Statement):
    token: Token; name: Identifier; params: List[Tuple[Identifier, TypeNode]]
    return_type: TypeNode; capture_fields: List[Tuple[Identifier, TypeNode]]
    body: BlockStatement; is_flow: bool = False
    def token_literal(self) -> str: return self.token.literal

@dataclass
class StructDefinition(Statement):
    token: Token; name: Identifier; fields: List[Tuple[Identifier, TypeNode]]
    def token_literal(self) -> str: return self.token.literal # [修正] 补上此方法