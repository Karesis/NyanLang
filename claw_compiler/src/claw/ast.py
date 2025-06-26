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

"""
Abstract Syntax Tree (AST) node definitions for the Nyanlang.

This module defines all node types used in the AST, including expressions,
statements, type nodes, and declarations. Each node is represented as a dataclass
and implements the Node interface.
"""

# --- 基础接口 ---

class Node(ABC):

    @abstractmethod
    def token_literal(self) -> str: 
        pass

    def __str__(self) -> str: 
        return f"<{self.__class__.__name__}>"

class Statement(Node): 
    pass
class Expression(Node): 
    pass

# --- 根节点 ---
@dataclass
class Program(Node):
    """
    Represents the root node of the AST.
    """
    statements: List[Statement]

    def token_literal(self) -> str: 
        return self.statements[0].token_literal() if self.statements else ""

# --- Expression Nodes ---

@dataclass
class Identifier(Expression):
    """
    Represents an identifier (variable or function name) in the AST.

    Attributes:
        token (Token): The token corresponding to the identifier.
        value (str): The name of the identifier.

    Example:
        For the source code: `x = 5`

        The identifier node for `x` would be:
        ```
            Identifier(token=Token(TokenType.IDENT, "x"), value="x")
        ```
    """
    token: Token
    value: str

    def token_literal(self) -> str: 
        return self.token.literal
    
    def __str__(self) -> str: 
        return self.value

@dataclass
class IntegerLiteral(Expression):
    """
    Represents an integer literal in the AST.

    Attributes:
        token (Token): The token corresponding to the integer literal.
        value (int): The value of the integer literal.

    Example:
        For the source code: `x: i32 = 42`

        The integer literal node for `42` would be:
        ```
            IntegerLiteral(token=Token(TokenType.INTEGER, "42"), value=42)
        ```
    """
    token: Token
    value: int

    def token_literal(self) -> str: 
        return self.token.literal

    def __str__(self) -> str: 
        return str(self.value)

# --- 复杂表达式节点 ---
@dataclass
class PrefixExpression(Expression):
    """
    Represents a prefix expression in the AST.
    """
    token: Token
    operator: str
    right: Expression

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class InfixExpression(Expression):
    """
    Represents an infix (binary) expression in the AST, such as addition or comparison.

    Attributes:
        token (Token): 
            The operator token (e.g., '+').
        left (Expression): 
            The left-hand side expression.
        operator (str): 
            The operator as a string (e.g., '+', '-', '*', '/').
        right (Expression): 
            The right-hand side expression.

    Example:
        For the source code: `a + b`

        The infix expression node would be:
        ```
            InfixExpression(
                token=Token(TokenType.PLUS, "+"),
                left=Identifier(token=..., value="a"),
                operator="+",
                right=Identifier(token=..., value="b")
            )
        ```
    """
    token: Token
    left: Expression
    operator: str
    right: Expression

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class CallExpression(Expression):
    token: Token
    function: Expression
    arguments: List[Expression]

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class MemberAccessExpression(Expression):
    token: Token
    object: Expression
    field: Identifier

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class AssignmentExpression(Expression):
    token: Token
    left: Expression
    value: Expression
    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class StructLiteral(Expression):
    token: Token
    type_name: Identifier
    members: List[Tuple[Identifier, Expression]]
    
    def token_literal(self) -> str: 
        return self.token.literal

# --- 类型节点 ---
@dataclass
class TypeNode(Node):
    token: Token
    name: str

    def token_literal(self) -> str: 
        return self.token.literal

    def __str__(self) -> str: 
        return self.name

# --- 语句节点 ---
@dataclass
class ExpressionStatement(Statement):
    token: Token
    expression: Expression
    
    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class BlockStatement(Statement):
    token: Token
    statements: List[Statement]

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class ReturnStatement(Statement):
    """
    Represents a return statement in the AST.

    Attributes:
        token (Token): 
            The 'ret' keyword token.
        return_value (Expression): 
            The expression to return.

    Example:
        For the source code: `ret x + 1`

        The return statement node would be:
        ```
            ReturnStatement(
                token=Token(TokenType.RET, "ret"),
                return_value=InfixExpression(...)
            )
        ```
    """
    token: Token
    return_value: Optional[Expression]

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier
    type: TypeNode
    value: Optional[Expression]

    def token_literal(self) -> str: 
        return self.token.literal

# --- 声明节点 ---
@dataclass
class FunctionDeclaration(Statement):
    """
    Represents a function declaration in the AST.

    Attributes:
        token (Token): 
            The 'def' keyword token.
        name (Identifier): 
            The function name.
        params (List[Tuple[Identifier, TypeNode]]): 
            List of parameter names and types.
        return_type (TypeNode): 
            The return type of the function.
        capture_fields (List[Tuple[Identifier, TypeNode]]): 
            Captured variables (for closures).
        body (BlockStatement): 
            The function body.
        is_flow (bool): 
            Whether this function is a flow function (default: False).

    Example:
        For the source code:
        ```
            def add(a: i32, b: i32): i32
            {  
                return a + b;
            }
        ```
        The function declaration node would be:
        ```
            FunctionDeclaration(
                token=Token(TokenType.DEF, "def"),
                name=Identifier(token=..., value="add"),
                params=[(Identifier(token=..., value="a"), TypeNode(token=..., name="i32")),
                        (Identifier(token=..., value="b"), TypeNode(token=..., name="i32"))],
                return_type=TypeNode(token=..., name="i32"),
                capture_fields=[],
                body=BlockStatement(...),
                is_flow=False
            )
        ```
    """
    token: Token
    name: Identifier
    params: List[Tuple[Identifier, TypeNode]]
    return_type: TypeNode
    capture_fields: List[Tuple[Identifier, TypeNode]]
    body: BlockStatement
    is_flow: bool = False

    def token_literal(self) -> str: 
        return self.token.literal

@dataclass
class StructDefinition(Statement):
    """
    Represents a struct definition in the AST.
    In Nyanlang, structs are defined using the `def` keyword followed by a list of fields.
    And the struct also means a type.

    Attributes:
        token (Token):  
            The 'struct' keyword token.
        name (Identifier): 
            The struct name.
        fields (List[Tuple[Identifier, TypeNode]]): 
            List of field names and types.

    Example:
        For the source code:
        ```
            def { x: i32, y: i32 } Point
        ```
        The struct definition node would be:
            StructDefinition(
                token=Token(TokenType.DEF, "def"),
                name=Identifier(token=..., value="Point"),
                fields=[
                    (Identifier(token=..., value="x"), TypeNode(token=..., name="i32")),
                    (Identifier(token=..., value="y"), TypeNode(token=..., name="i32"))
                ]
            )
    """
    token: Token
    name: Identifier
    fields: List[Tuple[Identifier, TypeNode]]

    def token_literal(self) -> str: 
        return self.token.literal