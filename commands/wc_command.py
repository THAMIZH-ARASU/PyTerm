from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem


class WcCommand(BaseCommand):
    """Count lines, words, and characters."""
    
    def __init__(self):
        super().__init__("wc", "Count lines, words, and characters")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        
        def count_text(text: str) -> tuple:
            lines = text.count('\n') if text else 0
            words = len(text.split()) if text else 0
            chars = len(text)
            return lines, words, chars
        
        if not args:
            # Count stdin
            lines, words, chars = count_text(stdin)
            return CommandResult(0, f"{lines:8d} {words:8d} {chars:8d}")
        
        total_lines = total_words = total_chars = 0
        output_lines = []
        
        for path in args:
            content = fs.read_file(path)
            if content is None:
                return CommandResult(1, "", f"wc: {path}: No such file or directory")
            
            lines, words, chars = count_text(content)
            total_lines += lines
            total_words += words
            total_chars += chars
            
            output_lines.append(f"{lines:8d} {words:8d} {chars:8d} {path}")
        
        if len(args) > 1:
            output_lines.append(f"{total_lines:8d} {total_words:8d} {total_chars:8d} total")
        
        return CommandResult(0, "\n".join(output_lines))