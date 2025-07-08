from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem

class RmCommand(BaseCommand):
    """Remove files and directories."""
    
    def __init__(self):
        super().__init__("rm", "Remove files and directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "rm: missing operand")
        
        errors = []
        for path in args:
            if not fs.remove(path):
                errors.append(f"rm: cannot remove '{path}': No such file or directory")
        
        if errors:
            return CommandResult(1, "", "\n".join(errors))
        
        return CommandResult(0)
