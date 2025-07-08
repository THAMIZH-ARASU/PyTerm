from typing import Dict, Optional

from commands import (BaseCommand, 
                      CatCommand, 
                      CdCommand, 
                      ClearCommand, 
                      DateCommand,
                      EchoCommand,
                      ExportCommand,
                      FindCommand,
                      GrepCommand,
                      HeadCommand,
                      HelpCommand,
                      HistoryCommand,
                      LsCommand,
                      MkdirCommand,
                      NanoCommand,
                      NeofetchCommand,
                      PwdCommand,
                      RmCommand,
                      SaveCommand,
                      SortCommand,
                      TailCommand,
                      TouchCommand,
                      WcCommand,
                      WhichCommand 
                    )


class CommandRegistry:
    """Registry for all available commands."""
    
    _commands: Dict[str, BaseCommand] = {}
    
    @classmethod
    def register(cls, command: BaseCommand):
        """Register a command."""
        cls._commands[command.name] = command
    
    @classmethod
    def get_command(cls, name: str) -> Optional[BaseCommand]:
        """Get a command by name."""
        return cls._commands.get(name)
    
    @classmethod
    def get_all_commands(cls) -> Dict[str, BaseCommand]:
        """Get all registered commands."""
        return cls._commands.copy()
    
    @classmethod
    def initialize_builtin_commands(cls):
        """Initialize all built-in commands."""
        commands = [
            LsCommand(),
            WcCommand(),
            SortCommand(),
            HeadCommand(),
            TailCommand(),
            FindCommand(),
            DateCommand(),
            WhichCommand(),
            ClearCommand(),
            NeofetchCommand(),
            CdCommand(),
            PwdCommand(),
            EchoCommand(),
            MkdirCommand(),
            CatCommand(),
            ExportCommand(),
            HistoryCommand(),
            TouchCommand(),
            RmCommand(),
            GrepCommand(),
            NanoCommand(),
            SaveCommand(),
            HelpCommand(),
        ]
        
        for cmd in commands:
            cls.register(cmd)