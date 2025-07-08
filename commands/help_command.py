
from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors

class HelpCommand(BaseCommand):
    """Show help for commands."""
    
    def __init__(self):
        super().__init__("help", "Show help for commands")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        
        from utils.command_registry import CommandRegistry  # Local import to avoid circular import

        if args:
            cmd_name = args[0]
            cmd = CommandRegistry.get_command(cmd_name)
            if cmd:
                return CommandResult(0, Colors.info(cmd.get_help()))
            else:
                return CommandResult(1, "", Colors.error(f"help: no help topics match '{cmd_name}'"))
        else:
            # Show all commands
            commands = CommandRegistry.get_all_commands()
            output = [Colors.highlight("Available commands:")]
            for cmd in commands.values():
                output.append(f"  {Colors.success(cmd.name):<12} {Colors.info(cmd.description)}")
            
            return CommandResult(0, "\n".join(output))
