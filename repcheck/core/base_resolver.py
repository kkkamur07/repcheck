from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Set, Optional

class BaseOrderResolver(ABC):
    """Abstract base class for dependency resolvers."""
    
    @abstractmethod
    def extract_file_dependencies(self, script_path: Path) -> Set[str]:
        """Extract file dependencies from script."""
        pass
    
    def build_dependency_graph(self, scripts: List[Path]) -> Dict[str, Set[str]]:
        """Build dependency graph (common implementation)."""
        graph = {}
        script_paths = {str(s.resolve()) for s in scripts}
        
        for script in scripts:
            script_key = str(script.resolve())
            deps = self.extract_file_dependencies(script)
            graph[script_key] = deps.intersection(script_paths)
        
        return graph
    
    def topological_sort(self, graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """Sort scripts in execution order (common implementation)."""
        in_degree = {node: 0 for node in graph}
        
        for node in graph:
            in_degree[node] = len(graph[node])
        
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        processed = set()
        
        while queue:
            current = queue.pop(0)
            
            if current in processed:
                continue
                
            result.append(current)
            processed.add(current)
            
            for node in graph:
                if current in graph[node] and node not in processed:
                    in_degree[node] -= 1
                    if in_degree[node] == 0 and node not in queue:
                        queue.append(node)
        
        if len(result) != len(graph):
            return None
        
        return result
    
    def resolve_execution_order(self, scripts: List[Path]) -> Dict:
        """Resolve execution order (common implementation)."""
        graph = self.build_dependency_graph(scripts)
        execution_order = self.topological_sort(graph)
        
        return {
            "total_scripts": len(scripts),
            "dependency_graph": {k: list(v) for k, v in graph.items()},
            "execution_order": execution_order,
            "has_circular_dependency": execution_order is None
        }