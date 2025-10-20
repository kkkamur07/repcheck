import re
import ast
from pathlib import Path
from typing import Set

from repcheck.core.base_resolver import BaseOrderResolver

class PythonScriptOrderResolver(BaseOrderResolver):
    """Resolve execution order of Python scripts based on dependencies."""
    
    def extract_file_dependencies(self, script_path: Path) -> Set[str]:
        """Extract file dependencies from Python script (import statements)."""
        dependencies = set()
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the Python file
            tree = ast.parse(content)
            
            # Find relative imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    # Handle: from .module import something
                    if node.level > 0:  # Relative import
                        module_path = self._resolve_relative_import(script_path, node.module, node.level)
                        if module_path:
                            dependencies.add(str(module_path))
                
                elif isinstance(node, ast.Import):
                    # Handle: import module
                    for alias in node.names:
                        # Try to resolve as local module
                        module_path = self._resolve_local_import(script_path, alias.name)
                        if module_path:
                            dependencies.add(str(module_path))
        
        except Exception:
            pass
        
        return dependencies
    
    def _resolve_relative_import(self, script_path: Path, module: str, level: int) -> Path:
        """Resolve relative import to absolute path."""
        # level indicates how many directories to go up
        base_dir = script_path.parent
        for _ in range(level - 1):
            base_dir = base_dir.parent
        
        if module:
            module_file = base_dir / f"{module.replace('.', '/')}.py"
        else:
            module_file = base_dir / "__init__.py"
        
        if module_file.exists():
            return module_file.resolve()
        return None
    
    def _resolve_local_import(self, script_path: Path, module_name: str) -> Path:
        """Try to resolve import as local module in same directory."""
        script_dir = script_path.parent
        
        # Check if module exists as .py file in same directory
        module_file = script_dir / f"{module_name}.py"
        if module_file.exists():
            return module_file.resolve()
        
        # Check if module exists as package
        module_package = script_dir / module_name / "__init__.py"
        if module_package.exists():
            return module_package.resolve()
        
        return None