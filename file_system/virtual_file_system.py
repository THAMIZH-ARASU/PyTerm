
import json
import os
from typing import List, Optional
from file_system.file import FileNode


class VirtualFileSystem:
    """Manages the virtual file system."""
    
    def __init__(self):
        self.root = FileNode("", is_directory=True)
        self.current_path = "/"
        self.storage_file = "terminal_filesystem.json"
        self._load_filesystem()
        if not self._filesystem_exists():
            self._setup_initial_structure()
            self._save_filesystem()
    
    def _filesystem_exists(self) -> bool:
        """Check if filesystem data file exists."""
        try:
            return os.path.exists(self.storage_file)
        except:
            return False
    
    def _save_filesystem(self):
        """Save filesystem state to JSON file."""
        try:
            data = {
                'current_path': self.current_path,
                'root': self._serialize_node(self.root)
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save filesystem: {e}")
    
    def _load_filesystem(self):
        """Load filesystem state from JSON file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_path = data.get('current_path', '/home/user')
                    self.root = self._deserialize_node(data.get('root', {}))
        except Exception as e:
            print(f"Warning: Could not load filesystem: {e}")
            # Fallback to default structure
            self.current_path = "/home/user"
            self.root = FileNode("", is_directory=True)
    
    def _serialize_node(self, node: FileNode) -> dict:
        """Serialize a FileNode to dictionary."""
        data = {
            'name': node.name,
            'content': node.content,
            'is_directory': node.is_directory,
            'permissions': node.permissions,
            'size': node.size
        }
        if node.is_directory and node.children:
            data['children'] = {name: self._serialize_node(child) 
                              for name, child in node.children.items()}
        return data
    
    def _deserialize_node(self, data: dict) -> FileNode:
        """Deserialize dictionary to FileNode."""
        node = FileNode(
            name=data.get('name', ''),
            content=data.get('content', ''),
            is_directory=data.get('is_directory', False),
            permissions=data.get('permissions', 'rwxr-xr-x'),
            size=data.get('size', 0)
        )
        
        if node.is_directory and 'children' in data:
            node.children = {}
            for name, child_data in data['children'].items():
                node.children[name] = self._deserialize_node(child_data)
        
        return node
    
    def _setup_initial_structure(self):
        """Set up initial directory structure."""
        self.mkdir("/home")
        self.mkdir("/home/user")
        self.mkdir("/tmp")
        self.mkdir("/var")
        self.mkdir("/usr")
        self.mkdir("/usr/bin")
        self.current_path = "/home/user"
    
    def _get_node(self, path: str) -> Optional[FileNode]:
        """Get node at given path."""
        if path == "/":
            return self.root
        
        parts = path.strip("/").split("/")
        current = self.root
        
        for part in parts:
            if not part:
                continue
            if not current.is_directory or part not in current.children:
                return None
            current = current.children[part]
        
        return current
    
    def _resolve_path(self, path: str) -> str:
        """Resolve relative path to absolute path."""
        if path.startswith("/"):
            return path
        
        if path == ".":
            return self.current_path
        
        if path == "..":
            if self.current_path == "/":
                return "/"
            return "/".join(self.current_path.rstrip("/").split("/")[:-1]) or "/"
        
        if self.current_path == "/":
            return f"/{path}"
        return f"{self.current_path}/{path}"
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        resolved = self._resolve_path(path)
        return self._get_node(resolved) is not None
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory."""
        resolved = self._resolve_path(path)
        node = self._get_node(resolved)
        return node is not None and node.is_directory
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        resolved = self._resolve_path(path)
        node = self._get_node(resolved)
        return node is not None and not node.is_directory
    
    def mkdir(self, path: str) -> bool:
        """Create directory."""
        resolved = self._resolve_path(path)
        if self.exists(resolved):
            return False
        
        parent_path = "/".join(resolved.rstrip("/").split("/")[:-1]) or "/"
        parent = self._get_node(parent_path)
        
        if parent is None or not parent.is_directory:
            return False
        
        dir_name = resolved.split("/")[-1]
        parent.children[dir_name] = FileNode(dir_name, is_directory=True)
        self._save_filesystem()
        return True
    
    def touch(self, path: str, content: str = "") -> bool:
        """Create or update file."""
        resolved = self._resolve_path(path)
        parent_path = "/".join(resolved.rstrip("/").split("/")[:-1]) or "/"
        parent = self._get_node(parent_path)
        
        if parent is None or not parent.is_directory:
            return False
        
        file_name = resolved.split("/")[-1]
        parent.children[file_name] = FileNode(file_name, content=content)
        self._save_filesystem()
        return True
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content."""
        resolved = self._resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None or node.is_directory:
            return None
        
        return node.content
    
    def write_file(self, path: str, content: str, append: bool = False) -> bool:
        """Write to file."""
        resolved = self._resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None:
            return self.touch(path, content)
        
        if node.is_directory:
            return False
        
        if append:
            node.content += content
        else:
            node.content = content
        
        node.size = len(node.content)
        self._save_filesystem()
        return True
    
    def list_directory(self, path: str = None) -> List[FileNode]:
        """List directory contents."""
        if path is None:
            path = self.current_path
        
        resolved = self._resolve_path(path)
        node = self._get_node(resolved)
        
        if node is None or not node.is_directory:
            return []
        
        return list(node.children.values())
    
    def change_directory(self, path: str) -> bool:
        """Change current directory."""
        resolved = self._resolve_path(path)
        
        if not self.is_directory(resolved):
            return False
        
        self.current_path = resolved
        self._save_filesystem()
        return True
    
    def remove(self, path: str) -> bool:
        """Remove file or directory."""
        resolved = self._resolve_path(path)
        if resolved == "/":
            return False
        
        parent_path = "/".join(resolved.rstrip("/").split("/")[:-1]) or "/"
        parent = self._get_node(parent_path)
        
        if parent is None or not parent.is_directory:
            return False
        
        item_name = resolved.split("/")[-1]
        if item_name in parent.children:
            del parent.children[item_name]
            self._save_filesystem()
            return True
        
        return False
