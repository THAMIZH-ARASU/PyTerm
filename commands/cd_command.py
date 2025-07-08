from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class CdCommand(BaseCommand):
    """Change directory."""
    
    def __init__(self):
        super().__init__("cd", "Change directory")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        path = args[0] if args else env.get_variable("HOME")
        
        if fs.change_directory(path):
            env.set_variable("PWD", fs.current_path)
            return CommandResult(0)
        else:
            return CommandResult(1, "", f"cd: {path}: No such file or directory")