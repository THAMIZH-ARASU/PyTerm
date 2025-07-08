
class CommandResult:
    """Represents the result of a command execution."""
    
    def __init__(self, exit_code: int = 0, output: str = "", error: str = ""):
        self.exit_code = exit_code
        self.output = output
        self.error = error
    
    @property
    def success(self) -> bool:
        return self.exit_code == 0