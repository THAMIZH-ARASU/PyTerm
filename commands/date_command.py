import datetime
from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors


class DateCommand(BaseCommand):
    """Display current date and time."""
    
    def __init__(self):
        super().__init__("date", "Display current date and time")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        now = datetime.datetime.now()
        return CommandResult(0, Colors.highlight(now.strftime("%a %b %d %H:%M:%S %Y")))