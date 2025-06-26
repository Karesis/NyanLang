# src/claw/parser/utils.py
"""
此模块定义了 Parser 所需的辅助常量，例如 Token 的优先级。
"""
from enum import IntEnum
from ..token import TokenType

class Precedence(IntEnum):
    """定义了运算符的优先级，数值越大，优先级越高。"""
    (
        LOWEST, 
        EQUALS, 
        LESSGREATER, 
        SUM, 
        PRODUCT, 
        PREFIX, 
        CALL, 
        MEMBER
    ) = range(8)

# 优先级映射表
precedences = {
    TokenType.ASSIGN: Precedence.EQUALS,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACE: Precedence.CALL, # 用于 struct literal
    TokenType.DOT: Precedence.MEMBER,
}