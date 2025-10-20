import os
import shlex
import subprocess
from pathlib import Path
from time import perf_counter
from typing import List, Dict, Any

from repcheck.core.base_checker import BaseScriptChecker

class PythonScriptChecker(BaseScriptChecker):
    """Python script checker with linting and execution."""
    
    def find_scripts(self, root: Path, patterns: List[str], exclude: List[str]) -> List[Path]:
        """Find Python scripts matching patterns."""
        found: List[Path] = []
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                p = Path(dirpath) / fn
                if not any(p.match(pat) for pat in patterns):
                    continue
                if any(p.match(pat) for pat in exclude):
                    continue
                found.append(p)
        return sorted(found)
    
    def lint_script(self, path: Path) -> Dict[str, Any]:
        """Lint Python script using flake8."""
        try:
            result = subprocess.run(
                ['flake8', str(path), '--max-line-length=100'], 
                capture_output=True, text=True, timeout=30
            )
            
            return {
                "path": str(path),
                "lint_passed": result.returncode == 0,
                "lint_output": result.stdout + result.stderr if result.returncode != 0 else "No linting issues found"
            }
        except FileNotFoundError:
            # flake8 not installed, skip linting
            return {
                "path": str(path),
                "lint_passed": True,
                "lint_output": "flake8 not available, skipping lint"
            }
        except Exception as e:
            return {
                "path": str(path),
                "lint_passed": False,
                "lint_output": f"Linting failed: {str(e)}"
            }
    
    def run_script(self, path: Path) -> Dict[str, Any]:
        """Execute Python script and return results."""
        script_dir = path.parent
        script_name = path.name
        
        cmd = ["python3", script_name]
        t0 = perf_counter()
        
        try:
            res = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                cwd=script_dir
            )
            dur = perf_counter() - t0
            return {
                "path": str(path),
                "cmd": shlex.join(cmd),
                "code": res.returncode,
                "duration": round(dur, 3),
                "stdout": res.stdout,
                "stderr": res.stderr,
                "execution_passed": res.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "path": str(path),
                "code": 124,
                "duration": self.timeout,
                "stderr": f"Timed out after {self.timeout}s",
                "execution_passed": False
            }