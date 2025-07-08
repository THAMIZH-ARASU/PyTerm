from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors


class PwdCommand(BaseCommand):
    """Print working directory."""
    
    def __init__(self):
        super().__init__("pwd", "Print working directory")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        return CommandResult(0, Colors.info(fs.current_path))
