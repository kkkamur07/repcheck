from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class BaseScriptChecker(ABC):
    """Abstract base class for all script checkers."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    @abstractmethod
    def find_scripts(self, root: Path, patterns: List[str], exclude: List[str]) -> List[Path]:
        """Find scripts matching patterns."""
        pass
    
    @abstractmethod
    def lint_script(self, path: Path) -> Dict[str, Any]:
        """Lint a script."""
        pass
    
    @abstractmethod
    def run_script(self, path: Path) -> Dict[str, Any]:
        """Execute a script."""
        pass
    
    def check_script(self, path: Path, lint: bool = True) -> Dict[str, Any]:
        """Check a single script (common implementation)."""
        result = {"path": str(path)}
        
        if lint:
            lint_result = self.lint_script(path)
            result.update(lint_result)
        
        exec_result = self.run_script(path)
        result.update(exec_result)
        
        if lint:
            result["overall_passed"] = result.get("lint_passed", False) and result["execution_passed"]
        else:
            result["overall_passed"] = result["execution_passed"]
        
        return result
    
    def check_all(self, root: Path, patterns: List[str], exclude: List[str], 
                  lint: bool = True) -> Dict[str, Any]:
        """Check all scripts in project (common implementation)."""
        scripts = self.find_scripts(root, patterns, exclude)
        
        if not scripts:
            return {"scripts_found": 0, "results": []}
        
        results = []
        for script in scripts:
            result = self.check_script(script, lint)
            results.append(result)
        
        total = len(results)
        passed = sum(1 for r in results if r["overall_passed"])
        
        return {
            "root": str(root),
            "scripts_found": total,
            "results": results,
            "passed": passed,
            "failed": total - passed
        }