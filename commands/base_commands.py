from abc import ABC, abstractmethod
from typing import List

from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class BaseCommand(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        """Execute the command."""
        pass
    
    def get_help(self) -> str:
        """Get help text for the command."""
        return f"{self.name}: {self.description}"