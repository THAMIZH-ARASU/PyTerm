# Terminal Emulator - Complete Implementation
# File: main.py






















































# =============================================================================
# TERMINAL INTERFACE
# =============================================================================

class TerminalInterface:
    """Main terminal interface."""
    
    def __init__(self):
        self.fs = VirtualFileSystem()
        self.env = EnvironmentManager()
        self.executor = CommandExecutor(self.fs, self.env)
        self.history_file = os.path.expanduser("~/.terminal_history")
        
        # Initialize commands
        CommandRegistry.initialize_builtin_commands()
        
        # Set up readline
        self._setup_readline()
    
    def _setup_readline(self):
        """Set up readline for command history and completion."""
        if not READLINE_AVAILABLE:
            return  # Skip readline setup on Windows
        
        try:
            # Load history
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
            
            # Set up completion
            readline.set_completer(self._complete)
            readline.parse_and_bind("tab: complete")
            
            # Save history on exit
            atexit.register(self._save_history)
            
        except (ImportError, OSError):
            pass  # readline not available
    
    def _save_history(self):
        """Save command history to file."""
        if not READLINE_AVAILABLE:
            return  # Skip history save on Windows
        
        try:
            readline.write_history_file(self.history_file)
        except (ImportError, OSError):
            pass
    
    def _complete(self, text: str, state: int) -> Optional[str]:
        """Tab completion function."""
        if not READLINE_AVAILABLE:
            return None  # No completion on Windows
        
        if state == 0:
            # Get current line
            line = readline.get_line_buffer()
            
            # Simple completion: complete command names
            if not line or line.count(" ") == 0:
                commands = list(CommandRegistry.get_all_commands().keys())
                self._matches = [cmd for cmd in commands if cmd.startswith(text)]
            else:
                # Complete filenames
                try:
                    files = self.fs.list_directory()
                    self._matches = [f.name for f in files if f.name.startswith(text)]
                except:
                    self._matches = []
        
        try:
            return self._matches[state]
        except IndexError:
            return None
    
    def get_prompt(self) -> str:
        """Get the command prompt."""
        user = self.env.get_variable("USER") or "user"
        path = self.fs.current_path
        if path == f"/home/{user}":
            path = "~"
        return f"{Colors.success(user)}:{Colors.info(path)}{Colors.highlight('$')} "
    
    def run(self):
        """Main terminal loop."""
        print(Colors.highlight("Terminal Emulator v1.0"))
        print(Colors.info("Persistent filesystem enabled - your files and settings will be saved automatically."))
        print(f"Type {Colors.success('help')} for available commands, {Colors.success('exit')} to quit.")
        print()
        
        while True:
            try:
                # Get command input
                prompt = self.get_prompt()
                command_line = input(prompt)
                
                # Handle built-in exit
                if command_line.strip().lower() in ["exit", "quit"]:
                    print(Colors.success("Goodbye!"))
                    break
                
                # Add to history
                self.env.add_to_history(command_line)
                
                # Execute command
                result = self.executor.execute_command_line(command_line)
                
                # Display output
                if result.output:
                    print(result.output)
                
                # Display errors
                if result.error:
                    print(f"Error: {result.error}", file=sys.stderr)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.warning('Keyboard interrupt')}")
                continue
            except EOFError:
                print(f"\n{Colors.success('Goodbye!')}")
                break
            except Exception as e:
                print(f"{Colors.error(f'Unexpected error: {e}')}", file=sys.stderr)

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    try:
        terminal = TerminalInterface()
        terminal.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

# =============================================================================
# EXAMPLE USAGE AND TESTS
# =============================================================================

def run_tests():
    """Run basic tests."""
    print("Running basic tests...")
    
    # Test file system
    fs = VirtualFileSystem()
    assert fs.mkdir("/test")
    assert fs.touch("/test/file.txt", "Hello World")
    assert fs.read_file("/test/file.txt") == "Hello World"
    assert fs.is_directory("/test")
    assert fs.is_file("/test/file.txt")

if __name__ == "__main__":
    main()

