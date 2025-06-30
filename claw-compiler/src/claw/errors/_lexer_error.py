from ._base import ClawError

class LexerError(ClawError):
    """
    Indicates an error during the lexing (tokenization) phase.
    For example, an unrecognized character.
    """
    pass
