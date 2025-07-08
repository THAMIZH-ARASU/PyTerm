# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text."""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        """Color for success messages."""
        return Colors.colorize(text, Colors.BRIGHT_GREEN)
    
    @staticmethod
    def error(text: str) -> str:
        """Color for error messages."""
        return Colors.colorize(text, Colors.RED)
    
    @staticmethod
    def warning(text: str) -> str:
        """Color for warning messages."""
        return Colors.colorize(text, Colors.YELLOW)
    
    @staticmethod
    def info(text: str) -> str:
        """Color for info messages."""
        return Colors.colorize(text, Colors.BRIGHT_CYAN)
    
    @staticmethod
    def highlight(text: str) -> str:
        """Color for highlighted text."""
        return Colors.colorize(text, Colors.BRIGHT_MAGENTA)