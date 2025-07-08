from errors.terminal_error import TerminalError


class CommandNotFoundError(TerminalError):
    """Raised when a command is not found."""
    pass