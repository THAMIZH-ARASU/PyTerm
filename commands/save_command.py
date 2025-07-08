from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors

class SaveCommand(BaseCommand):
    """Manually save filesystem and environment state."""
    
    def __init__(self):
        super().__init__("save", "Save filesystem and environment state")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        try:
            fs._save_filesystem()
            env._save_environment()
            return CommandResult(0, Colors.success("Filesystem and environment saved successfully!"))
        except Exception as e:
            return CommandResult(1, "", Colors.error(f"save: error - {str(e)}"))