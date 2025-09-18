import re
from pathlib import Path
from typing import List, Dict, Set, Optional

class RScriptOrderResolver:
    """Resolve execution order of R scripts based on dependencies."""
    
    def __init__(self):
        pass
    
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
    
    def build_dependency_graph(self, scripts: List[Path]) -> Dict[str, Set[str]]:
        """Build dependency graph - key depends on values."""
        graph = {}
        script_paths = {str(s.resolve()) for s in scripts}
        
        for script in scripts:
            script_key = str(script.resolve())
            deps = self.extract_file_dependencies(script)
            # Only include dependencies that are in our script list
            graph[script_key] = deps.intersection(script_paths)
        
        return graph
    
    def topological_sort(self, graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """Sort scripts so dependencies run before dependents."""
        in_degree = {node: 0 for node in graph}
        
        # Count how many scripts each script depends on
        for node in graph:
            in_degree[node] = len(graph[node])
        
        # Start with scripts that have no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # For each script that depends on current script
            for node in graph:
                if current in graph[node]:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        # Check for circular dependencies
        if len(result) != len(graph):
            return None
        
        return result
    
    def resolve_execution_order(self, scripts: List[Path]) -> Dict:
        """Resolve the execution order of R scripts."""
        graph = self.build_dependency_graph(scripts)
        execution_order = self.topological_sort(graph)
        
        result = {
            "total_scripts": len(scripts),
            "dependency_graph": {k: list(v) for k, v in graph.items()},
            "execution_order": execution_order,
            "has_circular_dependency": execution_order is None
        }
        
        if execution_order is None:
            result["error"] = "Circular dependency detected"
        
        return result
    
    def get_script_dependencies(self, script_path: Path, all_scripts: List[Path]) -> Dict:
        """Get dependencies for a single script."""
        deps = self.extract_file_dependencies(script_path)
        script_paths = {str(s.resolve()) for s in all_scripts}
        
        valid_deps = []
        missing_deps = []
        
        for dep in deps:
            if dep in script_paths:
                valid_deps.append(dep)
            else:
                missing_deps.append(dep)
        
        return {
            "script": str(script_path.resolve()),
            "dependencies": valid_deps,
            "missing_files": missing_deps,
            "dependency_count": len(valid_deps)
        }