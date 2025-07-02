"""
Makes the main Parser class and its factory function available for import
directly from the 'claw.parser' package.

Usage:
    from claw.parser import create_parser, Parser
    from claw.lexer import Lexer

    lexer = Lexer("my_var := 5")
    parser = create_parser(lexer)
    program = parser.parse_program()
"""
from .main import Parser
from .factory import create_parser

__all__ = ["Parser", "create_parser"]