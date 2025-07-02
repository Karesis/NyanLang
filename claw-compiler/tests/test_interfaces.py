"""
Unit tests for the abstract base classes (interfaces) of the parser.
"""
import pytest
from claw.parser.interfaces import PrefixParselet, InfixParselet
from claw.parser.precedence import Precedence
from claw.parser import Parser
from claw.tokens import Token
from claw import ast

def test_prefix_parselet_interface_raises_error():
    """
    Ensures that calling the abstract `parse` method on PrefixParselet's
    base class correctly raises NotImplementedError.
    """
    class ConcreteButErroneousPrefix(PrefixParselet):
        def parse(self, parser: Parser, token: Token): 
            # Explicitly call the super-class method to trigger the error.
            return super().parse(parser, token) # type: ignore

    instance = ConcreteButErroneousPrefix()
    with pytest.raises(NotImplementedError):
        # We need dummy arguments to call the method.
        instance.parse(None, None) # type: ignore

def test_infix_parselet_interface_raises_errors():
    """
    Ensures that calling the abstract methods on InfixParselet's
    base class correctly raises NotImplementedError.
    """
    class ConcreteButErroneousInfix(InfixParselet):
        # Implement all abstract methods, but have them call super()
        def parse(self, parser: Parser, left: ast.Expression, token: Token): 
            return super().parse(parser, left, token) # type: ignore
        
        @property
        def precedence(self) -> Precedence:
            return super().precedence # type: ignore

    instance = ConcreteButErroneousInfix()
    with pytest.raises(NotImplementedError):
        instance.parse(None, None, None) # type: ignore
    
    with pytest.raises(NotImplementedError):
        _ = instance.precedence
