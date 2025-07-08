from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.command_registry import CommandRegistry


class WhichCommand(BaseCommand):
    """Locate commands."""
    
    def __init__(self):
        super().__init__("which", "Locate commands")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "which: missing command name")
        
        results = []
        for cmd_name in args:
            if CommandRegistry.get_command(cmd_name):
                results.append(f"/usr/bin/{cmd_name}")
            else:
                return CommandResult(1, "", f"which: {cmd_name}: command not found")
        
        return CommandResult(0, "\n".join(results))