from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from errors.file_system_error import FileSystemError
from errors.invalid_argument_error import InvalidArgumentError

class HeadCommand(BaseCommand):
    """Display first lines of files."""
    
    def __init__(self):
        super().__init__("head", "Display first lines of files")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        num_lines = 10
        files = []
        
        # Parse arguments
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-n" and i + 1 < len(args):
                try:
                    num_lines = int(args[i + 1])
                    i += 1
                except ValueError:
                    raise InvalidArgumentError(f"head: invalid number '{args[i + 1]}'")
            elif arg.startswith("-n"):
                try:
                    num_lines = int(arg[2:])
                except ValueError:
                    raise InvalidArgumentError(f"head: invalid number '{arg[2:]}'")
            elif arg.startswith("-"):
                raise InvalidArgumentError(f"head: invalid option '{arg}'")
            else:
                files.append(arg)
            i += 1
        
        # Get text to process
        if files:
            output_parts = []
            for file_path in files:
                content = fs.read_file(file_path)
                if content is None:
                    raise FileSystemError(f"head: {file_path}: No such file or directory")
                lines = content.split('\n')
                selected_lines = lines[:num_lines]
                if len(files) > 1:
                    output_parts.append(f"==> {file_path} <==")
                    output_parts.append('\n'.join(selected_lines))
                else:
                    output_parts.append('\n'.join(selected_lines))
            return CommandResult(0, '\n'.join(output_parts))
        else:
            lines = stdin.split('\n') if stdin else []
            selected_lines = lines[:num_lines]
            return CommandResult(0, '\n'.join(selected_lines))