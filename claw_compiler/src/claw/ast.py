# src/claw/ast.py

"""
Abstract Syntax Tree (AST) node definitions for the Nyan programming language.

This module defines all node types that the parser produces. These nodes form
a tree structure that represents the parsed source code. Key node types include
expressions, statements, and declarations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .token import Token

# --- Type Aliases for Readability ---

# A type alias for a list of fields, commonly used in struct and function definitions.
# Each item is a tuple of (identifier, type_node).
FieldList = list[tuple["Identifier", "TypeNode"]]


# --- Base Interfaces ---

class Node(ABC):
    """The base class for all AST nodes."""

    @abstractmethod
    def token_literal(self) -> str:
        """
        Returns the literal value of the token associated with this node.
        Used for debugging and error reporting.
        """
        pass

    def __str__(self) -> str:
        """Provides a default string representation for the node."""
        return f"<{self.__class__.__name__}>"


class Statement(Node):
    """A base class for all statement nodes."""
    pass


class Expression(Node):
    """A base class for all expression nodes."""
    pass


# --- Root Node ---

@dataclass(frozen=True)
class Program(Node):
    """
    Represents the root node of the AST, containing a sequence of statements.
    """
    statements: list[Statement]

    def token_literal(self) -> str:
        """Returns the token literal of the first statement, if one exists."""
        return self.statements[0].token_literal() if self.statements else ""

    def __str__(self) -> str:
        """Returns a string representation of all statements in the program."""
        return "".join(str(s) for s in self.statements)


# --- Expression Nodes ---

@dataclass(frozen=True)
class Identifier(Expression):
    """Represents an identifier (e.g., a variable or function name)."""
    token: Token  # The TokenType.IDENT token
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class IntegerLiteral(Expression):
    """Represents an integer literal."""
    token: Token  # The TokenType.INTEGER token
    value: int

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class PrefixExpression(Expression):
    """Represents a prefix expression, like '-x' or '!y'."""
    token: Token     # The prefix token, e.g., '!' or '-'
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"


@dataclass(frozen=True)
class InfixExpression(Expression):
    """Represents an infix expression, like 'x + y'."""
    token: Token     # The operator token, e.g., '+'
    left: Expression
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


@dataclass(frozen=True)
class CallExpression(Expression):
    """Represents a function call expression."""
    token: Token                # The '(' token
    function: Expression        # Identifier or other expression that evaluates to a function
    arguments: list[Expression]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.function}({args})"


@dataclass(frozen=True)
class MemberAccessExpression(Expression):
    """Represents accessing a member of a struct, e.g., 'point.x'."""
    token: Token        # The '.' token
    object: Expression  # The expression being accessed (the struct instance)
    field: Identifier   # The field being accessed

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.object}.{self.field})"


@dataclass(frozen=True)
class AssignmentExpression(Expression):
    """Represents an assignment, e.g., 'x = 5' or 'point.y = 10'."""
    token: Token        # The '=' token
    left: Expression    # The l-value being assigned to
    value: Expression   # The r-value being assigned

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.left} = {self.value})"


@dataclass(frozen=True)
class StructLiteral(Expression):
    """Represents the instantiation of a struct, e.g., 'Point{x: 1, y: 2}'."""
    token: Token      # The '{' token
    type_name: Identifier
    members: list[tuple[Identifier, Expression]]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        members_str = ", ".join(f"{k}: {v}" for k, v in self.members)
        return f"{self.type_name}{{{members_str}}}"


# --- Type Nodes ---

@dataclass(frozen=True)
class TypeNode(Node):
    """Represents a type annotation in the source code, e.g., 'i32' or 'Point'."""
    token: Token  # The token for the type name
    name: str

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.name


# --- Statement Nodes ---

@dataclass(frozen=True)
class ExpressionStatement(Statement):
    """A statement consisting of a single expression, e.g., 'x + 10;'."""
    token: Token       # The first token of the expression
    expression: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return str(self.expression)


@dataclass(frozen=True)
class BlockStatement(Statement):
    """Represents a block of statements enclosed in curly braces '{}'."""
    token: Token  # The '{' token
    statements: list[Statement]

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class ReturnStatement(Statement):
    """Represents a return statement, e.g., 'ret x;'."""
    token: Token                   # The 'ret' token
    return_value: Expression | None  # The expression to return, or None for 'ret;'

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class LetStatement(Statement):
    """Represents a variable declaration, e.g., 'p: Point = ...'."""
    token: Token                   # The identifier token of the variable name
    name: Identifier
    type: TypeNode
    value: Expression | None       # The initializer expression, optional for some scenarios

    def token_literal(self) -> str:
        return self.token.literal


# --- Declaration Nodes ---

@dataclass(frozen=True)
class FunctionDeclaration(Statement):
    """Represents a function declaration."""
    token: Token         # The 'def' token
    name: Identifier
    params: FieldList
    return_type: TypeNode
    capture_fields: FieldList
    body: BlockStatement
    is_flow: bool = False

    def token_literal(self) -> str:
        return self.token.literal


@dataclass(frozen=True)
class StructDefinition(Statement):
    """Represents a struct type definition."""
    token: Token       # The 'def' token
    name: Identifier
    fields: FieldList

    def token_literal(self) -> str:
        return self.token.literal
