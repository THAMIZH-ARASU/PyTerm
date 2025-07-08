from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class FileNode:
    """Represents a file in the virtual file system."""
    name: str
    content: str = ""
    is_directory: bool = False
    permissions: str = "rwxr-xr-x"
    size: int = 0
    children: Optional[Dict[str, 'FileNode']] = None
    
    def __post_init__(self):
        if self.is_directory and self.children is None:
            self.children = {}
        if not self.is_directory:
            self.size = len(self.content)