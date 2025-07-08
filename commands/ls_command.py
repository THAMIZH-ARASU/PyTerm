from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors
from errors.file_system_error import FileSystemError


class LsCommand(BaseCommand):
    """List directory contents."""
    
    def __init__(self):
        super().__init__("ls", "List directory contents")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        path = args[0] if args else None
        
        try:
            files = fs.list_directory(path)
            if not files:
                return CommandResult(0, "")
            
            # Format output
            output_lines = []
            for file in files:
                # Format: permissions size user group name
                permissions = file.permissions
                size = file.size
                name = file.name
                
                # Color coding for different file types
                if file.is_directory:
                    name = Colors.highlight(name + "/")
                    permissions = Colors.info(permissions)
                else:
                    name = Colors.success(name)
                    permissions = Colors.warning(permissions)
                
                size_str = Colors.info(f"{size:8d}")
                
                output_lines.append(f"{permissions} {size_str} {name}")
            
            return CommandResult(0, "\n".join(output_lines))
            
        except Exception as e:
            raise FileSystemError(f"ls: {str(e)}")