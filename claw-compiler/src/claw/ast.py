"""
Defines the Abstract Syntax Tree (AST) nodes for the NyanLang language.

Each node in the tree represents a construct in the source code. The parser's
goal is to produce a tree of these nodes from a stream of tokens. This AST
then serves as the input for later stages of the compiler, such as the
interpreter or code generator.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from .tokens import Token, TokenType


# =============================================================================
# 1. Base Interfaces
# =============================================================================

class Node(ABC):
    """The base class for all AST nodes."""

    @abstractmethod
    def token_literal(self) -> str:
        """
        Returns the literal value of the token associated with this node.
        Used primarily for debugging and testing.
        """
        raise NotImplementedError


class Statement(Node):
    """A base class for statement nodes, which do not produce a value."""
    pass


class Expression(Node):
    """A base class for expression nodes, which produce a value."""
    pass


# =============================================================================
# 2. Type Nodes
#    Represents type annotations, e.g., 'x: i32' or '-> ~f64{...}'
# =============================================================================

class TypeNode(Node):
    """The base class for all type annotation nodes."""
    pass


@dataclass(frozen=True)
class SimpleType(TypeNode):
    """Represents a simple type, such as i32, f64, or string."""
    token: Token  # The token for the type name, e.g., IDENTIFIER("i32")

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class MutableType(TypeNode):
    """Represents a mutable type, such as `~i32`."""
    token: Token      # The '~' token
    base_type: TypeNode # The underlying type, e.g., SimpleType("i32")

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class StructTypeLiteral(TypeNode):
    """Represents an anonymous struct type, e.g., `{x: i32, y: i32}`."""
    token: Token  # The '{' token
    fields: dict[Identifier, TypeNode]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class CompositeType(TypeNode):
    """Represents a composite return type, e.g., `i32{x: i32}`."""
    token: Token        # The token of the primary type
    primary_type: TypeNode
    struct_type: StructTypeLiteral

    def token_literal(self) -> str:
        return self.token.literal


# =============================================================================
# 3. Root Node
# =============================================================================

@dataclass(frozen=True)
class Program(Node):
    """The root node of every AST, representing a complete NyanLang program."""
    statements: list[Statement]

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()
        return ""


# =============================================================================
# 4. Expressions
# =============================================================================

@dataclass(frozen=True)
class Identifier(Expression):
    """Represents an identifier, such as a variable or function name."""
    token: Token  # The IDENTIFIER token
    value: str

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class IntegerLiteral(Expression):
    """Represents an integer literal, such as `123`."""
    token: Token
    value: int

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class FloatLiteral(Expression):
    """Represents a floating-point literal, such as `1.23`."""
    token: Token
    value: float

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class StringLiteral(Expression):
    """Represents a string literal, such as `"hello"`."""
    token: Token
    value: str

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class BooleanLiteral(Expression):
    """Represents a boolean literal, `true` or `false`."""
    token: Token  # The 'true' or 'false' token
    value: bool

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class PrefixExpression(Expression):
    """Represents a prefix expression, such as `-5` or `!true`."""
    token: Token    # The prefix operator token, e.g., '!' or '-'
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class InfixExpression(Expression):
    """Represents an infix expression, such as `x + y`."""
    token: Token     # The infix operator token, e.g., '+'
    left: Expression
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class AssignmentExpression(Expression):
    """Represents a mutable assignment, such as `z = 7`."""
    token: Token  # The '=' token
    name: Identifier
    value: Expression

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class IfExpression(Expression):
    """Represents an if-else expression."""
    token: Token  # The 'if' token
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement | None = None

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class LoopExpression(Expression):
    """Represents an infinite loop expression."""
    token: Token  # The 'loop' token
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class WhileExpression(Expression):
    """Represents a while-loop expression."""
    token: Token  # The 'while' token
    condition: Expression
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class FunctionLiteral(Expression):
    """Represents a function definition, e.g., `add(x: i32) -> i32 { ... }`."""
    token: Token  # The opening '(' token of the parameter list
    name: Identifier | None
    parameters: list[Identifier]
    param_types: dict[Identifier, TypeNode]
    return_type: TypeNode | None
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class CallExpression(Expression):
    """Represents a function call, e.g., `add(1, 2)`."""
    token: Token          # The opening '(' of the argument list
    function: Expression  # Identifier or FunctionLiteral being called
    arguments: list[Expression]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class StructLiteral(Expression):
    """Represents a struct instantiation, e.g., `Point{x: 4, y: 7}`."""
    token: Token  # The name of the struct type
    name: Identifier
    fields: dict[Identifier, Expression]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class MemberAccessExpression(Expression):
    """Represents a member access, e.g., `P.x`."""
    token: Token  # The '.' token
    object: Expression
    property: Identifier

    def token_literal(self) -> str:
        return self.token.literal


# =============================================================================
# 5. Statements
# =============================================================================

@dataclass(frozen=True)
class BlockStatement(Statement):
    """Represents a block of code enclosed in curly braces, `{ ... }`."""
    token: Token  # The '{' token
    statements: list[Statement]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class LetStatement(Statement):
    """Represents a variable declaration, e.g., `x: i32 := 5`."""
    token: Token      # The identifier token
    name: Identifier
    value_type: TypeNode | None
    value: Expression | None

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class ReturnStatement(Statement):
    """Represents a return statement, `ret ...`."""
    token: Token  # The 'ret' token
    return_value: Expression | None

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class BreakStatement(Statement):
    """Represents a break statement from a loop, `break ...`."""
    token: Token  # The 'break' token
    return_value: Expression | None

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class ContinueStatement(Statement):
    """Represents a continue statement in a loop, `con ...`."""
    token: Token  # The 'con' token
    return_value: Expression | None

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class DefStatement(Statement):
    """Represents a struct definition, e.g., `def { ... } Point`."""
    token: Token  # The 'def' token
    name: Identifier
    fields: dict[Identifier, TypeNode]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class FlowStatement(Statement):
    """Represents a flow definition, e.g., `@my_flow { ... }`."""
    token: Token  # The '@' token
    name: Identifier
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class ExpressionStatement(Statement):
    """
    Wraps an expression to be used as a statement.
    e.g., a function call on its own line: `my_flow;`
    """
    expression: Expression

    @property
    def token(self) -> Token:
        """The token is the first token of the contained expression."""
        # This is a bit of a special case. To get the token, we need to
        # access the expression's token. We can't store it directly in the
        # dataclass since it's derived data.
        current_node = self.expression
        while isinstance(current_node, ExpressionStatement):
             current_node = current_node.expression
        # Now current_node is guaranteed to be a non-ExpressionStatement node
        # which will have a 'token' attribute.
        return getattr(current_node, 'token', Token(TokenType.ILLEGAL, "", 0, 0))

    def token_literal(self) -> str:
        return self.expression.token_literal()