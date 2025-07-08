from errors.terminal_error import TerminalError


class InvalidArgumentError(TerminalError):
    """Raised when command arguments are invalid."""
    pass