from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors


class CatCommand(BaseCommand):
    """Display file contents."""
    
    def __init__(self):
        super().__init__("cat", "Display file contents")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(0, stdin)
        
        # Check for redirection
        redirect_args = []
        normal_args = []
        
        for arg in args:
            if arg.startswith('>') or arg.startswith('>>') or arg.startswith('<'):
                redirect_args.append(arg)
            else:
                normal_args.append(arg)
        
        # Handle redirection
        if redirect_args:
            for redirect_arg in redirect_args:
                if redirect_arg.startswith('>'):
                    # Output redirection
                    if redirect_arg.startswith('>>'):
                        # Append mode
                        filename = redirect_arg[2:]
                        if not fs.write_file(filename, stdin, append=True):
                            return CommandResult(1, "", Colors.error(f"cat: cannot write to '{filename}'"))
                    else:
                        # Overwrite mode
                        filename = redirect_arg[1:]
                        if not fs.write_file(filename, stdin):
                            return CommandResult(1, "", Colors.error(f"cat: cannot write to '{filename}'"))
                elif redirect_arg.startswith('<'):
                    # Input redirection
                    filename = redirect_arg[1:]
                    content = fs.read_file(filename)
                    if content is None:
                        return CommandResult(1, "", Colors.error(f"cat: {filename}: No such file or directory"))
                    return CommandResult(0, Colors.success(content))
            
            # If we had redirection, we're done
            return CommandResult(0)
        
        # Normal cat behavior - read files and display content
        if not normal_args:
            return CommandResult(0, stdin)
        
        output_lines = []
        for path in normal_args:
            content = fs.read_file(path)
            if content is None:
                return CommandResult(1, "", Colors.error(f"cat: {path}: No such file or directory"))
            output_lines.append(Colors.success(content))
        
        return CommandResult(0, "\n".join(output_lines))