class ClawError(Exception):
    """
    The base class for all errors that can occur during the
    compilation process in the Claw compiler.
    
    It stores the error message and the position in the source
    code where the error occurred.
    """
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        # Format a user-friendly error message, which the base Exception class will use
        super().__init__(f"[Line {line}, Col {column}] Error: {message}")