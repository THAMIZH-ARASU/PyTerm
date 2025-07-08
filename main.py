# Terminal Emulator - Complete Implementation
# File: main.py

import os
import sys
import atexit
from typing import Dict, List, Optional, Any, IO
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import re
import shlex
import signal
import threading
import time
from enum import Enum
import json
import fnmatch
import datetime

# Try to import readline, but don't fail if it's not available (Windows)
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

# Try to import psutil for system information
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False




# =============================================================================
# ENVIRONMENT MANAGER
# =============================================================================

class EnvironmentManager:
    """Manages environment variables and shell state."""
    
    def __init__(self):
        self.variables: Dict[str, str] = {
            "PATH": "/usr/bin:/bin",
            "HOME": "/home/user",
            "USER": "user",
            "SHELL": "/bin/terminal",
            "PS1": "$ ",
        }
        self.history: List[str] = []
        self.max_history = 1000
        self.env_file = "terminal_environment.json"
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables and history from file."""
        try:
            if os.path.exists(self.env_file):
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.variables.update(data.get('variables', {}))
                    self.history = data.get('history', [])
        except Exception as e:
            print(f"Warning: Could not load environment: {e}")
    
    def _save_environment(self):
        """Save environment variables and history to file."""
        try:
            data = {
                'variables': self.variables,
                'history': self.history
            }
            with open(self.env_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save environment: {e}")
    
    def set_variable(self, name: str, value: str):
        """Set environment variable."""
        self.variables[name] = value
        self._save_environment()
    
    def get_variable(self, name: str) -> Optional[str]:
        """Get environment variable."""
        return self.variables.get(name)
    
    def expand_variables(self, text: str) -> str:
        """Expand environment variables in text."""
        def replacer(match):
            var_name = match.group(1)
            return self.variables.get(var_name, f"${var_name}")
        
        return re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', replacer, text)
    
    def add_to_history(self, command: str):
        """Add command to history."""
        if command.strip():
            self.history.append(command)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self._save_environment()
    
    def get_history(self) -> List[str]:
        """Get command history."""
        return self.history.copy()

# =============================================================================
# COMMAND FRAMEWORK
# =============================================================================

class CommandResult:
    """Represents the result of a command execution."""
    
    def __init__(self, exit_code: int = 0, output: str = "", error: str = ""):
        self.exit_code = exit_code
        self.output = output
        self.error = error
    
    @property
    def success(self) -> bool:
        return self.exit_code == 0

class BaseCommand(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        """Execute the command."""
        pass
    
    def get_help(self) -> str:
        """Get help text for the command."""
        return f"{self.name}: {self.description}"

# =============================================================================
# BUILT-IN COMMANDS
# =============================================================================

class LsCommand(BaseCommand):
    """List directory contents."""
    
    def __init__(self):
        super().__init__("ls", "List directory contents")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        path = args[0] if args else None
        
        try:
            files = fs.list_directory(path)
            if not files:
                return CommandResult(0, "")
            
            # Format output
            output_lines = []
            for file in files:
                # Format: permissions size user group name
                permissions = file.permissions
                size = file.size
                name = file.name
                
                # Color coding for different file types
                if file.is_directory:
                    name = Colors.highlight(name + "/")
                    permissions = Colors.info(permissions)
                else:
                    name = Colors.success(name)
                    permissions = Colors.warning(permissions)
                
                size_str = Colors.info(f"{size:8d}")
                
                output_lines.append(f"{permissions} {size_str} {name}")
            
            return CommandResult(0, "\n".join(output_lines))
            
        except Exception as e:
            return CommandResult(1, "", f"ls: {str(e)}")

# =============================================================================
# ADDITIONAL UTILITY COMMANDS
# =============================================================================

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
                    return CommandResult(1, "", f"head: invalid number '{args[i + 1]}'")
            elif arg.startswith("-n"):
                try:
                    num_lines = int(arg[2:])
                except ValueError:
                    return CommandResult(1, "", f"head: invalid number '{arg[2:]}'")
            elif arg.startswith("-"):
                return CommandResult(1, "", f"head: invalid option '{arg}'")
            else:
                files.append(arg)
            i += 1
        
        # Get text to process
        if files:
            output_parts = []
            for file_path in files:
                content = fs.read_file(file_path)
                if content is None:
                    return CommandResult(1, "", f"head: {file_path}: No such file or directory")
                
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

class TailCommand(BaseCommand):
    """Display last lines of files."""
    
    def __init__(self):
        super().__init__("tail", "Display last lines of files")
    
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
                    return CommandResult(1, "", f"tail: invalid number '{args[i + 1]}'")
            elif arg.startswith("-n"):
                try:
                    num_lines = int(arg[2:])
                except ValueError:
                    return CommandResult(1, "", f"tail: invalid number '{arg[2:]}'")
            elif arg.startswith("-"):
                return CommandResult(1, "", f"tail: invalid option '{arg}'")
            else:
                files.append(arg)
            i += 1
        
        # Get text to process
        if files:
            output_parts = []
            for file_path in files:
                content = fs.read_file(file_path)
                if content is None:
                    return CommandResult(1, "", f"tail: {file_path}: No such file or directory")
                
                lines = content.split('\n')
                selected_lines = lines[-num_lines:] if len(lines) >= num_lines else lines
                
                if len(files) > 1:
                    output_parts.append(f"==> {file_path} <==")
                    output_parts.append('\n'.join(selected_lines))
                else:
                    output_parts.append('\n'.join(selected_lines))
            
            return CommandResult(0, '\n'.join(output_parts))
        else:
            lines = stdin.split('\n') if stdin else []
            selected_lines = lines[-num_lines:] if len(lines) >= num_lines else lines
            return CommandResult(0, '\n'.join(selected_lines))

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

class DateCommand(BaseCommand):
    """Display current date and time."""
    
    def __init__(self):
        super().__init__("date", "Display current date and time")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        now = datetime.datetime.now()
        return CommandResult(0, Colors.highlight(now.strftime("%a %b %d %H:%M:%S %Y")))

class WhichCommand(BaseCommand):
    """Locate commands."""
    
    def __init__(self):
        super().__init__("which", "Locate commands")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "which: missing command name")
        
        results = []
        for cmd_name in args:
            if CommandRegistry.get_command(cmd_name):
                results.append(f"/usr/bin/{cmd_name}")
            else:
                return CommandResult(1, "", f"which: {cmd_name}: command not found")
        
        return CommandResult(0, "\n".join(results))

class ClearCommand(BaseCommand):
    """Clear the terminal screen."""
    
    def __init__(self):
        super().__init__("clear", "Clear the terminal screen")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        # ANSI escape sequence to clear screen
        print("\033[2J\033[H", end="")
        return CommandResult(0)

class NeofetchCommand(BaseCommand):
    """Display system information in ASCII art format."""
    
    def __init__(self):
        super().__init__("neofetch", "Display system information")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        import platform
        
        # ASCII art logo (Linux-style)
        logo_lines = [
            "                  -`                   ",
            "                 .o+`                  ",
            "                `ooo/                  ",
            "               `+oooo:                 ",
            "              `+oooooo:                ",
            "              -+oooooo+:               ",
            "            `/:-:++oooo+:              ",
            "           `/++++/+++++++:             ",
            "          `/++++++++++++++:            ",
            "         `/+++ooooooooooooo/`          ",
            "        ./ooosssso++osssssso+`         ",
            "       .oossssso-````/ossssss+`        ",
            "      -osssssso.      :ssssssso.       ",
            "     :osssssss/        osssso+++.      ",
            "    /ossssssss/        +ssssooo/-      ",
            "  `/ossssso+/:-        -:/+osssso+-    ",
            " `+sso+:-`                 `.-/+oso:   ",
            "`++:.                           `-/+/  ",
            ".`                                 `/   "
        ]
        
        # System information
        info_lines = []
        
        # ANSI color codes for info
        colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bright_blue': '\033[94m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
        }
        
        # OS Information
        try:
            os_info = platform.system() + " " + platform.release()
            info_lines.append(f"{colors['bright_green']}OS{colors['reset']}: {colors['yellow']}{os_info}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}OS{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Python Version
        try:
            python_version = platform.python_version()
            info_lines.append(f"{colors['bright_green']}Python{colors['reset']}: {colors['yellow']}{python_version}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}Python{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # CPU Information
        if PSUTIL_AVAILABLE:
            try:
                cpu_count = psutil.cpu_count()
                cpu_percent = psutil.cpu_percent(interval=0.1)
                info_lines.append(f"{colors['bright_green']}CPU{colors['reset']}: {colors['yellow']}{cpu_count} cores{colors['reset']} ({colors['bright_cyan']}{cpu_percent:.1f}% usage{colors['reset']})")
            except:
                info_lines.append(f"{colors['bright_green']}CPU{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        else:
            info_lines.append(f"{colors['bright_green']}CPU{colors['reset']}: {colors['red']}psutil not available{colors['reset']}")
        
        # Memory Information
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                memory_total = memory.total / (1024**3)  # Convert to GB
                memory_used = memory.used / (1024**3)
                memory_percent = memory.percent
                info_lines.append(f"{colors['bright_green']}Memory{colors['reset']}: {colors['yellow']}{memory_used:.1f}GB / {memory_total:.1f}GB{colors['reset']} ({colors['bright_cyan']}{memory_percent:.1f}%{colors['reset']})")
            except:
                info_lines.append(f"{colors['bright_green']}Memory{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        else:
            info_lines.append(f"{colors['bright_green']}Memory{colors['reset']}: {colors['red']}psutil not available{colors['reset']}")
        
        # Disk Information
        if PSUTIL_AVAILABLE:
            try:
                disk = psutil.disk_usage('/')
                disk_total = disk.total / (1024**3)  # Convert to GB
                disk_used = disk.used / (1024**3)
                disk_percent = (disk.used / disk.total) * 100
                info_lines.append(f"{colors['bright_green']}Disk{colors['reset']}: {colors['yellow']}{disk_used:.1f}GB / {disk_total:.1f}GB{colors['reset']} ({colors['bright_cyan']}{disk_percent:.1f}%{colors['reset']})")
            except:
                info_lines.append(f"{colors['bright_green']}Disk{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        else:
            info_lines.append(f"{colors['bright_green']}Disk{colors['reset']}: {colors['red']}psutil not available{colors['reset']}")
        
        # Terminal Information
        try:
            terminal_size = os.get_terminal_size()
            info_lines.append(f"{colors['bright_green']}Terminal{colors['reset']}: {colors['yellow']}{terminal_size.columns}x{terminal_size.lines}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}Terminal{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Current Directory
        info_lines.append(f"{colors['bright_green']}Directory{colors['reset']}: {colors['yellow']}{fs.current_path}{colors['reset']}")
        
        # User Information
        user = env.get_variable("USER") or "user"
        info_lines.append(f"{colors['bright_green']}User{colors['reset']}: {colors['yellow']}{user}{colors['reset']}")
        
        # Additional Information
        try:
            # Hostname
            hostname = platform.node()
            info_lines.append(f"{colors['bright_green']}Hostname{colors['reset']}: {colors['yellow']}{hostname}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}Hostname{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Architecture
        try:
            arch = platform.machine()
            info_lines.append(f"{colors['bright_green']}Architecture{colors['reset']}: {colors['yellow']}{arch}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}Architecture{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Kernel Version
        try:
            kernel = platform.release()
            info_lines.append(f"{colors['bright_green']}Kernel{colors['reset']}: {colors['yellow']}{kernel}{colors['reset']}")
        except:
            info_lines.append(f"{colors['bright_green']}Kernel{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Uptime (if psutil available)
        if PSUTIL_AVAILABLE:
            try:
                uptime = psutil.boot_time()
                from datetime import datetime
                uptime_seconds = datetime.now().timestamp() - uptime
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                info_lines.append(f"{colors['bright_green']}Uptime{colors['reset']}: {colors['yellow']}{uptime_hours}h {uptime_minutes}m{colors['reset']}")
            except:
                info_lines.append(f"{colors['bright_green']}Uptime{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        else:
            info_lines.append(f"{colors['bright_green']}Uptime{colors['reset']}: {colors['red']}psutil not available{colors['reset']}")
        
        # Shell
        info_lines.append(f"{colors['bright_green']}Shell{colors['reset']}: {colors['yellow']}Terminal Emulator{colors['reset']}")
        
        # Resolution (if available)
        try:
            # Try multiple methods to get screen resolution
            resolution_found = False
            
            # Method 1: Using tkinter (most reliable)
            try:
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()  # Hide the window
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.destroy()
                info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['yellow']}{width}x{height}{colors['reset']}")
                resolution_found = True
            except:
                pass
            
            # Method 2: Using ctypes (Windows specific)
            if not resolution_found:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                    height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                    info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['yellow']}{width}x{height}{colors['reset']}")
                    resolution_found = True
                except:
                    pass
            
            # Method 3: Using subprocess with PowerShell
            if not resolution_found:
                try:
                    import subprocess
                    result = subprocess.run(['powershell', '-Command', 'Get-WmiObject -Class Win32_VideoController | Select-Object -First 1 | Select-Object CurrentHorizontalResolution, CurrentVerticalResolution'], 
                                          capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        output = result.stdout.strip()
                        if output and 'CurrentHorizontalResolution' in output:
                            lines = output.split('\n')
                            for line in lines:
                                if line.strip() and 'CurrentHorizontalResolution' not in line and 'CurrentVerticalResolution' not in line:
                                    parts = line.strip().split()
                                    if len(parts) >= 2:
                                        width, height = parts[0], parts[1]
                                        info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['yellow']}{width}x{height}{colors['reset']}")
                                        resolution_found = True
                                        break
                except:
                    pass
            
            # Method 4: Using wmic (fallback)
            if not resolution_found:
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'path', 'Win32_VideoController', 'get', 'CurrentHorizontalResolution,CurrentVerticalResolution'], 
                                          capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            res_line = lines[1].strip()
                            if res_line and res_line != 'CurrentHorizontalResolution  CurrentVerticalResolution':
                                parts = res_line.split()
                                if len(parts) >= 2:
                                    width, height = parts[0], parts[1]
                                    info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['yellow']}{width}x{height}{colors['reset']}")
                                    resolution_found = True
                except:
                    pass
            
            if not resolution_found:
                info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
                
        except:
            info_lines.append(f"{colors['bright_green']}Resolution{colors['reset']}: {colors['red']}Unknown{colors['reset']}")
        
        # Format the output with logo on left and info on right
        output_lines = []
        
        # ANSI color codes
        colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bright_blue': '\033[94m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
        }
        
        # Combine logo and info lines
        max_lines = max(len(logo_lines), len(info_lines))
        for i in range(max_lines):
            logo_part = logo_lines[i] if i < len(logo_lines) else " " * 40
            info_part = info_lines[i] if i < len(info_lines) else ""
            
            # Add the box around the info if it's the first few lines
            if i < 5:
                if i == 0:
                    info_part = f"{colors['cyan']}╭─────────────────────────────────────────────────────────────╮{colors['reset']}"
                elif i == 1:
                    info_part = f"{colors['cyan']}│                                                             │{colors['reset']}"
                elif i == 2:
                    info_part = f"{colors['cyan']}│{colors['reset']}                    {colors['bold']}{colors['bright_green']}Terminal Emulator{colors['reset']}{colors['cyan']}                        │{colors['reset']}"
                elif i == 3:
                    info_part = f"{colors['cyan']}│                                                             │{colors['reset']}"
                elif i == 4:
                    info_part = f"{colors['cyan']}╰─────────────────────────────────────────────────────────────╯{colors['reset']}"
            
            output_lines.append(f"{colors['bright_blue']}{logo_part}{colors['reset']}{info_part}")
        
        return CommandResult(0, "\n".join(output_lines))

class CdCommand(BaseCommand):
    """Change directory."""
    
    def __init__(self):
        super().__init__("cd", "Change directory")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        path = args[0] if args else env.get_variable("HOME")
        
        if fs.change_directory(path):
            env.set_variable("PWD", fs.current_path)
            return CommandResult(0)
        else:
            return CommandResult(1, "", f"cd: {path}: No such file or directory")

class PwdCommand(BaseCommand):
    """Print working directory."""
    
    def __init__(self):
        super().__init__("pwd", "Print working directory")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        return CommandResult(0, Colors.info(fs.current_path))

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

class MkdirCommand(BaseCommand):
    """Create directories."""
    
    def __init__(self):
        super().__init__("mkdir", "Create directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "mkdir: missing operand")
        
        errors = []
        for path in args:
            if not fs.mkdir(path):
                errors.append(f"mkdir: cannot create directory '{path}'")
        
        if errors:
            return CommandResult(1, "", "\n".join(errors))
        
        return CommandResult(0)

class CatCommand(BaseCommand):
    """Display file contents."""
    
    def __init__(self):
        super().__init__("cat", "Display file contents")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(0, stdin)
        
        # Check for redirection
        redirect_args = []
        normal_args = []
        
        for arg in args:
            if arg.startswith('>') or arg.startswith('>>') or arg.startswith('<'):
                redirect_args.append(arg)
            else:
                normal_args.append(arg)
        
        # Handle redirection
        if redirect_args:
            for redirect_arg in redirect_args:
                if redirect_arg.startswith('>'):
                    # Output redirection
                    if redirect_arg.startswith('>>'):
                        # Append mode
                        filename = redirect_arg[2:]
                        if not fs.write_file(filename, stdin, append=True):
                            return CommandResult(1, "", Colors.error(f"cat: cannot write to '{filename}'"))
                    else:
                        # Overwrite mode
                        filename = redirect_arg[1:]
                        if not fs.write_file(filename, stdin):
                            return CommandResult(1, "", Colors.error(f"cat: cannot write to '{filename}'"))
                elif redirect_arg.startswith('<'):
                    # Input redirection
                    filename = redirect_arg[1:]
                    content = fs.read_file(filename)
                    if content is None:
                        return CommandResult(1, "", Colors.error(f"cat: {filename}: No such file or directory"))
                    return CommandResult(0, Colors.success(content))
            
            # If we had redirection, we're done
            return CommandResult(0)
        
        # Normal cat behavior - read files and display content
        if not normal_args:
            return CommandResult(0, stdin)
        
        output_lines = []
        for path in normal_args:
            content = fs.read_file(path)
            if content is None:
                return CommandResult(1, "", Colors.error(f"cat: {path}: No such file or directory"))
            output_lines.append(Colors.success(content))
        
        return CommandResult(0, "\n".join(output_lines))

class ExportCommand(BaseCommand):
    """Set environment variables."""
    
    def __init__(self):
        super().__init__("export", "Set environment variables")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            # Show all variables
            output = []
            for name, value in env.variables.items():
                output.append(f"{name}={value}")
            return CommandResult(0, "\n".join(output))
        
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                env.set_variable(name, value)
            else:
                # Just export existing variable
                value = env.get_variable(arg)
                if value is not None:
                    env.set_variable(arg, value)
        
        return CommandResult(0)

class HistoryCommand(BaseCommand):
    """Show command history."""
    
    def __init__(self):
        super().__init__("history", "Show command history")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        history = env.get_history()
        output = []
        for i, cmd in enumerate(history, 1):
            output.append(f"{i:4d}  {cmd}")
        
        return CommandResult(0, "\n".join(output))

class TouchCommand(BaseCommand):
    """Create empty files."""
    
    def __init__(self):
        super().__init__("touch", "Create empty files")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "touch: missing file operand")
        
        for path in args:
            if not fs.touch(path):
                return CommandResult(1, "", f"touch: cannot create '{path}'")
        
        return CommandResult(0)

class RmCommand(BaseCommand):
    """Remove files and directories."""
    
    def __init__(self):
        super().__init__("rm", "Remove files and directories")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "rm: missing operand")
        
        errors = []
        for path in args:
            if not fs.remove(path):
                errors.append(f"rm: cannot remove '{path}': No such file or directory")
        
        if errors:
            return CommandResult(1, "", "\n".join(errors))
        
        return CommandResult(0)

class GrepCommand(BaseCommand):
    """Search for patterns in text."""
    
    def __init__(self):
        super().__init__("grep", "Search for patterns in text")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(1, "", "grep: missing pattern")
        
        pattern = args[0]
        
        if len(args) > 1:
            # Search in files
            output_lines = []
            for file_path in args[1:]:
                content = fs.read_file(file_path)
                if content is None:
                    return CommandResult(1, "", f"grep: {file_path}: No such file or directory")
                
                for line in content.split("\n"):
                    if pattern in line:
                        output_lines.append(line)
            
            return CommandResult(0, "\n".join(output_lines))
        else:
            # Search in stdin
            output_lines = []
            for line in stdin.split("\n"):
                if pattern in line:
                    output_lines.append(line)
            
            return CommandResult(0, "\n".join(output_lines))

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

class SaveCommand(BaseCommand):
    """Manually save filesystem and environment state."""
    
    def __init__(self):
        super().__init__("save", "Save filesystem and environment state")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        try:
            fs._save_filesystem()
            env._save_environment()
            return CommandResult(0, Colors.success("Filesystem and environment saved successfully!"))
        except Exception as e:
            return CommandResult(1, "", Colors.error(f"save: error - {str(e)}"))

class HelpCommand(BaseCommand):
    """Show help for commands."""
    
    def __init__(self):
        super().__init__("help", "Show help for commands")
    
    def execute(self, args: List[str], fs: VirtualFileSystem, 
                env: EnvironmentManager, stdin: str = "") -> CommandResult:
        
        if args:
            cmd_name = args[0]
            cmd = CommandRegistry.get_command(cmd_name)
            if cmd:
                return CommandResult(0, Colors.info(cmd.get_help()))
            else:
                return CommandResult(1, "", Colors.error(f"help: no help topics match '{cmd_name}'"))
        else:
            # Show all commands
            commands = CommandRegistry.get_all_commands()
            output = [Colors.highlight("Available commands:")]
            for cmd in commands.values():
                output.append(f"  {Colors.success(cmd.name):<12} {Colors.info(cmd.description)}")
            
            return CommandResult(0, "\n".join(output))

# =============================================================================
# COMMAND REGISTRY
# =============================================================================

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

# =============================================================================
# COMMAND PARSER
# =============================================================================

class TokenType(Enum):
    """Token types for command parsing."""
    WORD = "WORD"
    PIPE = "PIPE"
    AND = "AND"
    OR = "OR"
    SEMICOLON = "SEMICOLON"
    REDIRECT_OUT = "REDIRECT_OUT"
    REDIRECT_APPEND = "REDIRECT_APPEND"
    REDIRECT_IN = "REDIRECT_IN"

@dataclass
class Token:
    """Represents a token in command parsing."""
    type: TokenType
    value: str
    position: int

class CommandParser:
    """Parses command line input into executable commands."""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.position = 0
    
    def tokenize(self, input_text: str) -> List[Token]:
        """Tokenize input text."""
        tokens = []
        position = 0
        
        # Special operators
        operators = {
            "|": TokenType.PIPE,
            "&&": TokenType.AND,
            "||": TokenType.OR,
            ";": TokenType.SEMICOLON,
            ">>": TokenType.REDIRECT_APPEND,
            ">": TokenType.REDIRECT_OUT,
            "<": TokenType.REDIRECT_IN,
        }
        
        i = 0
        while i < len(input_text):
            char = input_text[i]
            
            # Skip whitespace
            if char.isspace():
                i += 1
                continue
            
            # Check for two-character operators
            if i + 1 < len(input_text):
                two_char = input_text[i:i+2]
                if two_char in operators:
                    tokens.append(Token(operators[two_char], two_char, i))
                    i += 2
                    continue
            
            # Check for single-character operators
            if char in operators:
                tokens.append(Token(operators[char], char, i))
                i += 1
                continue
            
            # Parse words (including quoted strings)
            if char in ['"', "'"]:
                quote_char = char
                word_start = i
                i += 1
                word = ""
                
                while i < len(input_text) and input_text[i] != quote_char:
                    word += input_text[i]
                    i += 1
                
                if i < len(input_text):
                    i += 1  # Skip closing quote
                
                tokens.append(Token(TokenType.WORD, word, word_start))
            else:
                # Regular word
                word_start = i
                word = ""
                
                while (i < len(input_text) and 
                       not input_text[i].isspace() and 
                       input_text[i] not in operators):
                    word += input_text[i]
                    i += 1
                
                if word:
                    tokens.append(Token(TokenType.WORD, word, word_start))
        
        return tokens
    
    def parse(self, input_text: str) -> List['CommandPipeline']:
        """Parse input text into command pipelines."""
        tokens = self.tokenize(input_text)
        pipelines = []
        
        current_pipeline = []
        current_command = []
        current_redirect = None
        
        for token in tokens:
            if token.type == TokenType.WORD:
                if current_redirect:
                    # This is the filename for redirection
                    current_command.append(f"{current_redirect.value}{token.value}")
                    current_redirect = None
                else:
                    current_command.append(token.value)
            elif token.type == TokenType.PIPE:
                if current_command:
                    current_pipeline.append(current_command)
                    current_command = []
            elif token.type in [TokenType.AND, TokenType.OR, TokenType.SEMICOLON]:
                if current_command:
                    current_pipeline.append(current_command)
                    current_command = []
                
                if current_pipeline:
                    pipelines.append(CommandPipeline(current_pipeline, token.type))
                    current_pipeline = []
            elif token.type in [TokenType.REDIRECT_OUT, TokenType.REDIRECT_APPEND, TokenType.REDIRECT_IN]:
                current_redirect = token
        
        # Handle remaining command
        if current_command:
            current_pipeline.append(current_command)
        
        if current_pipeline:
            pipelines.append(CommandPipeline(current_pipeline, TokenType.SEMICOLON))
        
        return pipelines

@dataclass
class CommandPipeline:
    """Represents a pipeline of commands."""
    commands: List[List[str]]
    operator: TokenType

# =============================================================================
# COMMAND EXECUTOR
# =============================================================================

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

