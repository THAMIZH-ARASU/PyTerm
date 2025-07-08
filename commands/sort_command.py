import re
from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem



class SortCommand(BaseCommand):
    """Sort lines of text."""
    
    def __init__(self):
        super().__init__("sort", "Sort lines of text")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        
        reverse = False
        numeric = False
        files = []
        
        # Parse arguments
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-r":
                reverse = True
            elif arg == "-n":
                numeric = True
            elif arg.startswith("-"):
                return CommandResult(1, "", f"sort: invalid option '{arg}'")
            else:
                files.append(arg)
            i += 1
        
        # Get text to sort
        if files:
            text_parts = []
            for file_path in files:
                content = fs.read_file(file_path)
                if content is None:
                    return CommandResult(1, "", f"sort: {file_path}: No such file or directory")
                text_parts.append(content)
            text = "\n".join(text_parts)
        else:
            text = stdin
        
        # Sort lines
        lines = text.split('\n') if text else []
        
        if numeric:
            def sort_key(line):
                try:
                    # Extract first number from line
                    match = re.search(r'-?\d+', line)
                    return int(match.group()) if match else 0
                except:
                    return 0
            lines.sort(key=sort_key, reverse=reverse)
        else:
            lines.sort(reverse=reverse)
        
        return CommandResult(0, "\n".join(lines))