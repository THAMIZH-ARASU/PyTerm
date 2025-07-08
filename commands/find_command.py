import fnmatch
from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class FindCommand(BaseCommand):
    """Find files and directories."""
    
    def __init__(self):
        super().__init__("find", "Find files and directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        
        if not args:
            return CommandResult(1, "", "find: missing starting point")
        
        start_path = args[0]
        name_pattern = None
        
        # Parse arguments
        i = 1
        while i < len(args):
            if args[i] == "-name" and i + 1 < len(args):
                name_pattern = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Find files recursively
        def find_recursive(path: str, results: List[str]):
            if not fs.exists(path):
                return
            
            results.append(path)
            
            if fs.is_directory(path):
                try:
                    files = fs.list_directory(path)
                    for file in files:
                        child_path = f"{path}/{file.name}".replace("//", "/")
                        find_recursive(child_path, results)
                except:
                    pass
        
        results = []
        find_recursive(start_path, results)
        
        # Filter by name pattern if provided
        if name_pattern:
            filtered_results = []
            for path in results:
                filename = path.split("/")[-1]
                if fnmatch.fnmatch(filename, name_pattern):
                    filtered_results.append(path)
            results = filtered_results
        
        return CommandResult(0, "\n".join(results))