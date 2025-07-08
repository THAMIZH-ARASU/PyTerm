from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors


class EchoCommand(BaseCommand):
    """Echo arguments."""
    
    def __init__(self):
        super().__init__("echo", "Echo arguments")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        # Check for redirection
        redirect_args = []
        normal_args = []
        
        for arg in args:
            if arg.startswith('>') or arg.startswith('>>') or arg.startswith('<'):
                redirect_args.append(arg)
            else:
                normal_args.append(arg)
        
        # Generate output
        text = " ".join(normal_args)
        expanded = env.expand_variables(text)
        output = Colors.success(expanded)
        
        # Handle redirection
        if redirect_args:
            for redirect_arg in redirect_args:
                if redirect_arg.startswith('>'):
                    # Output redirection
                    if redirect_arg.startswith('>>'):
                        # Append mode
                        filename = redirect_arg[2:]
                        if not fs.write_file(filename, output, append=True):
                            return CommandResult(1, "", Colors.error(f"echo: cannot write to '{filename}'"))
                    else:
                        # Overwrite mode
                        filename = redirect_arg[1:]
                        if not fs.write_file(filename, output):
                            return CommandResult(1, "", Colors.error(f"echo: cannot write to '{filename}'"))
                elif redirect_arg.startswith('<'):
                    # Input redirection (not typically used with echo)
                    filename = redirect_arg[1:]
                    content = fs.read_file(filename)
                    if content is None:
                        return CommandResult(1, "", Colors.error(f"echo: {filename}: No such file or directory"))
                    return CommandResult(0, Colors.success(content))
            
            # If we had redirection, we're done
            return CommandResult(0)
        
        return CommandResult(0, output)