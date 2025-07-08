from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class ExportCommand(BaseCommand):
    """Set environment variables."""
    
    def __init__(self):
        super().__init__("export", "Set environment variables")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            # Show all variables
            output = []
            for name, value in env.variables.items():
                output.append(f"{name}={value}")
            return CommandResult(0, "\n".join(output))
        
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                env.set_variable(name, value)
            else:
                # Just export existing variable
                value = env.get_variable(arg)
                if value is not None:
                    env.set_variable(arg, value)
        
        return CommandResult(0)
