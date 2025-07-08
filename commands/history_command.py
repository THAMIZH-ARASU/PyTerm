from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class HistoryCommand(BaseCommand):
    """Show command history."""
    
    def __init__(self):
        super().__init__("history", "Show command history")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        history = env.get_history()
        output = []
        for i, cmd in enumerate(history, 1):
            output.append(f"{i:4d}  {cmd}")
        
        return CommandResult(0, "\n".join(output))