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
