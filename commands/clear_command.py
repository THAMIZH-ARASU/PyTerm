from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class ClearCommand(BaseCommand):
    """Clear the terminal screen."""
    
    def __init__(self):
        super().__init__("clear", "Clear the terminal screen")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        # ANSI escape sequence to clear screen
        print("\033[2J\033[H", end="")
        return CommandResult(0)
