from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from errors.file_system_error import FileSystemError
from errors.invalid_argument_error import InvalidArgumentError


class MkdirCommand(BaseCommand):
    """Create directories."""
    
    def __init__(self):
        super().__init__("mkdir", "Create directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            raise InvalidArgumentError("mkdir: missing operand")
        
        for path in args:
            if not fs.mkdir(path):
                raise FileSystemError(f"mkdir: cannot create directory '{path}'")
        
        return CommandResult(0)