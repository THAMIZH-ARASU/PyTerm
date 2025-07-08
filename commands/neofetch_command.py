import os
from typing import List
from commands.base_commands import BaseCommand
from commands.command_result import CommandResult
from env_manager.environment_manager import EnvironmentManager
from file_system.virtual_file_system import VirtualFileSystem

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
