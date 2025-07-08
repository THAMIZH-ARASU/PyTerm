import sys
from interface.terminal_interface import TerminalInterface


def main():
    """Main entry point."""
    try:
        terminal = TerminalInterface()
        terminal.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()

