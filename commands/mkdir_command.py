from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class MkdirCommand(BaseCommand):
    """Create directories."""
    
    def __init__(self):
        super().__init__("mkdir", "Create directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "mkdir: missing operand")
        
        errors = []
        for path in args:
            if not fs.mkdir(path):
                errors.append(f"mkdir: cannot create directory '{path}'")
        
        if errors:
            return CommandResult(1, "", "\n".join(errors))
        
        return CommandResult(0)