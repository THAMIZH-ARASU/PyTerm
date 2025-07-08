# =============================================================================
# COMMAND EXECUTOR
# =============================================================================

from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem
from utils.command_parser import CommandParser, CommandPipeline, TokenType
from utils.command_registry import CommandRegistry


class CommandExecutor:
    """Executes parsed commands."""
    
    def __init__(self, fs: VirtualFileSystem, env: EnvironmentManager):
        self.fs = fs
        self.env = env
    
    def execute_pipeline(self, pipeline: CommandPipeline) -> CommandResult:
        """Execute a command pipeline."""
        if not pipeline.commands:
            return CommandResult(0)
        
        # Execute commands in pipeline
        stdin_data = ""
        last_result = None
        
        for i, cmd_args in enumerate(pipeline.commands):
            if not cmd_args:
                continue
            
            # Expand variables in arguments
            expanded_args = []
            for arg in cmd_args:
                expanded_args.append(self.env.expand_variables(arg))
            
            cmd_name = expanded_args[0]
            cmd_args = expanded_args[1:]
            
            # Get command
            command = CommandRegistry.get_command(cmd_name)
            if not command:
                return CommandResult(1, "", f"Command not found: {cmd_name}")
            
            # Execute command
            try:
                result = command.execute(cmd_args, self.fs, self.env, stdin_data)
                last_result = result
                
                # If not the last command in pipeline, pass output as stdin
                if i < len(pipeline.commands) - 1:
                    stdin_data = result.output
                
                # If command failed and we're in a pipeline, stop
                if not result.success and len(pipeline.commands) > 1:
                    break
                    
            except Exception as e:
                return CommandResult(1, "", str(e))
        
        return last_result or CommandResult(0)
    
    def execute_command_line(self, command_line: str) -> CommandResult:
        """Execute a complete command line."""
        if not command_line.strip():
            return CommandResult(0)
        
        # Parse command line
        parser = CommandParser()
        pipelines = parser.parse(command_line)
        
        if not pipelines:
            return CommandResult(0)
        
        # Execute pipelines
        last_result = None
        for pipeline in pipelines:
            result = self.execute_pipeline(pipeline)
            last_result = result
            
            # Handle operators between pipelines
            if pipeline.operator == TokenType.AND and not result.success:
                break
            elif pipeline.operator == TokenType.OR and result.success:
                break
        
        return last_result or CommandResult(0)