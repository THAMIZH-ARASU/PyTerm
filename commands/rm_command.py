from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from errors.file_system_error import FileSystemError
from errors.invalid_argument_error import InvalidArgumentError

class RmCommand(BaseCommand):
    """Remove files and directories."""
    
    def __init__(self):
        super().__init__("rm", "Remove files and directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            raise InvalidArgumentError("rm: missing operand")
        
        for path in args:
            if not fs.remove(path):
                raise FileSystemError(f"rm: cannot remove '{path}': No such file or directory")
        
        return CommandResult(0)
