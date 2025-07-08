from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class GrepCommand(BaseCommand):
    """Search for patterns in text."""
    
    def __init__(self):
        super().__init__("grep", "Search for patterns in text")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "grep: missing pattern")
        
        pattern = args[0]
        
        if len(args) > 1:
            # Search in files
            output_lines = []
            for file_path in args[1:]:
                content = fs.read_file(file_path)
                if content is None:
                    return CommandResult(1, "", f"grep: {file_path}: No such file or directory")
                
                for line in content.split("\n"):
                    if pattern in line:
                        output_lines.append(line)
            
            return CommandResult(0, "\n".join(output_lines))
        else:
            # Search in stdin
            output_lines = []
            for line in stdin.split("\n"):
                if pattern in line:
                    output_lines.append(line)
            
            return CommandResult(0, "\n".join(output_lines))