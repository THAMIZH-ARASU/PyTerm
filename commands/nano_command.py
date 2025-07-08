from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.color import Colors


class NanoCommand(BaseCommand):
    """Simple text editor simulation."""
    
    def __init__(self):
        super().__init__("nano", "Simple text editor")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", Colors.error("nano: missing file operand"))
        
        filename = args[0]
        
        # Check if file exists
        existing_content = fs.read_file(filename)
        if existing_content is None:
            # Create new file
            existing_content = ""
        
        # Simple nano-like interface
        print(Colors.highlight(f"\n=== Nano Editor - {filename} ==="))
        print(Colors.info("Type your text. Press Ctrl+D (or Ctrl+Z on Windows) to save and exit."))
        print(Colors.info("Press Ctrl+C to cancel without saving."))
        print(Colors.colorize("─" * 50, Colors.CYAN))
        
        try:
            lines = []
            if existing_content:
                print(Colors.success("Existing content:"))
                for line in existing_content.split('\n'):
                    print(f"  {line}")
                print()
            
            print(Colors.warning("Enter new content (Ctrl+D to finish):"))
            
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print(f"\n{Colors.warning('Cancelled - no changes saved')}")
                    return CommandResult(1, "", "")
            
            # Save the file
            content = '\n'.join(lines)
            if fs.write_file(filename, content):
                print(f"\n{Colors.success(f'File {filename} saved successfully!')}")
                return CommandResult(0, f"Saved {len(lines)} lines to {filename}")
            else:
                return CommandResult(1, "", Colors.error(f"nano: cannot write to '{filename}'"))
                
        except Exception as e:
            return CommandResult(1, "", Colors.error(f"nano: error - {str(e)}"))