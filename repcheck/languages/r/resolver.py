import re
from pathlib import Path
from typing import Set

from repcheck.core.base_resolver import BaseOrderResolver

class RScriptOrderResolver(BaseOrderResolver):
    """Resolve execution order of R scripts based on dependencies."""
    
    def extract_file_dependencies(self, script_path: Path) -> Set[str]:
        """Extract file dependencies from R script (source() calls)."""
        dependencies = set()
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find source() calls
            source_pattern = r'source\s*\(\s*["\']([^"\']+)["\']'
            matches = re.findall(source_pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Convert to Path and resolve relative to script location
                dep_path = Path(match)
                if not dep_path.is_absolute():
                    dep_path = script_path.parent / dep_path
                dependencies.add(str(dep_path.resolve()))
        
        except Exception:
            pass
        
        return dependencies