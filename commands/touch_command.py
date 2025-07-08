from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from errors.file_system_error import FileSystemError
from errors.invalid_argument_error import InvalidArgumentError


class TouchCommand(BaseCommand):
    """Create empty files."""
    
    def __init__(self):
        super().__init__("touch", "Create empty files")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            raise InvalidArgumentError("touch: missing file operand")
        
        for path in args:
            if not fs.touch(path):
                raise FileSystemError(f"touch: cannot create '{path}'")
        
        return CommandResult(0)