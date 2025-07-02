"""
Provides a factory function to create and configure a fully-featured Parser instance.
"""
from ..lexer import Lexer
from ..tokens import TokenType
from .main import Parser
from .interfaces import PrefixParselet, InfixParselet
from .precedence import Precedence

# Import all concrete parselet classes
from .expressions.literal import (
    IdentifierParselet,
    IntegerLiteralParselet,
    FloatLiteralParselet,
    StringLiteralParselet,
    BooleanLiteralParselet,
)
from .expressions.prefix import PrefixOperatorParselet
from .expressions.infix import InfixOperatorParselet
from .expressions.group import GroupedExpressionParselet
from .expressions.call import CallExpressionParselet
from .expressions.member import MemberAccessParselet
from .expressions.assignment import AssignmentParselet
from .expressions._if import IfParselet  

def create_parser(lexer: Lexer) -> Parser:
    """
    Creates a new Parser instance, configured with all the parselets that
    define the NyanLang language grammar for expressions.
    """
    prefix_parselets: dict[TokenType, PrefixParselet] = {}
    infix_parselets: dict[TokenType, InfixParselet] = {}

    # --- Register Prefix Parselets ---
    prefix_parselets[TokenType.IDENTIFIER] = IdentifierParselet()
    prefix_parselets[TokenType.INTEGER] = IntegerLiteralParselet()
    prefix_parselets[TokenType.FLOAT] = FloatLiteralParselet()
    prefix_parselets[TokenType.STRING] = StringLiteralParselet()
    prefix_parselets[TokenType.TRUE] = BooleanLiteralParselet()
    prefix_parselets[TokenType.FALSE] = BooleanLiteralParselet()
    prefix_parselets[TokenType.LPAREN] = GroupedExpressionParselet()
    prefix_parselets[TokenType.MINUS] = PrefixOperatorParselet()
    prefix_parselets[TokenType.IF] = IfParselet()  

    # --- Register Infix Parselets ---
    infix_parselets[TokenType.ASSIGN] = AssignmentParselet()
    infix_parselets[TokenType.EQUALS] = InfixOperatorParselet(Precedence.EQUALS)
    infix_parselets[TokenType.NOT_EQUALS] = InfixOperatorParselet(Precedence.EQUALS)
    infix_parselets[TokenType.LT] = InfixOperatorParselet(Precedence.LESSGREATER)
    infix_parselets[TokenType.GT] = InfixOperatorParselet(Precedence.LESSGREATER)
    infix_parselets[TokenType.LTE] = InfixOperatorParselet(Precedence.LESSGREATER)
    infix_parselets[TokenType.GTE] = InfixOperatorParselet(Precedence.LESSGREATER)
    infix_parselets[TokenType.PLUS] = InfixOperatorParselet(Precedence.SUM)
    infix_parselets[TokenType.MINUS] = InfixOperatorParselet(Precedence.SUM)
    infix_parselets[TokenType.SLASH] = InfixOperatorParselet(Precedence.PRODUCT)
    infix_parselets[TokenType.ASTERISK] = InfixOperatorParselet(Precedence.PRODUCT)
    infix_parselets[TokenType.LPAREN] = CallExpressionParselet()
    infix_parselets[TokenType.DOT] = MemberAccessParselet()

    parser = Parser(
        lexer=lexer,
        prefix_parselets=prefix_parselets,
        infix_parselets=infix_parselets
    )
    return parser
