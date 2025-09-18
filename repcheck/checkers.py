import os
import json
import shlex
import subprocess
from pathlib import Path
from time import perf_counter
from typing import List, Dict, Any

class RScriptChecker:
    """Simple R script checker with proper linting."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    def find_scripts(self, root: Path, patterns: List[str], exclude: List[str]) -> List[Path]:
        """Find R scripts matching patterns."""
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
        """Lint R script using lintr package."""
        # Simple R command to run lintr
        r_cmd = f'''
        if (requireNamespace("lintr", quietly = TRUE)) {{
            results <- lintr::lint("{path}")
            if (length(results) > 0) {{
                for (r in results) print(r)
                quit(status = 1)
            }} else {{
                cat("No linting issues found\\n")
            }}
        }} else {{
            cat("lintr package not available\\n")
        }}
        '''
        
        try:
            result = subprocess.run(
                ['Rscript', '-e', r_cmd], 
                capture_output=True, text=True, timeout=30
            )
            
            return {
                "path": str(path),
                "lint_passed": result.returncode == 0,
                "lint_output": result.stdout + result.stderr
            }
        except Exception as e:
            return {
                "path": str(path),
                "lint_passed": False,
                "lint_output": f"Linting failed: {str(e)}"
            }
    
    def run_script(self, path: Path) -> Dict[str, Any]:
        """Execute R script and return results."""
        # Change to script's directory so relative paths work
        script_dir = path.parent
        script_name = path.name
        
        cmd = ["Rscript", "--vanilla", script_name]
        t0 = perf_counter()
        
        try:
            res = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                cwd=script_dir  # Run from script's directory
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
    
    def check_script(self, path: Path, lint: bool = True) -> Dict[str, Any]:
        """Check a single R script."""
        result = {"path": str(path)}
        
        if lint:
            lint_result = self.lint_script(path)
            result.update(lint_result)
        
        exec_result = self.run_script(path)
        result.update(exec_result)
        
        # Overall pass = lint passed AND execution passed
        if lint:
            result["overall_passed"] = result.get("lint_passed", False) and result["execution_passed"]
        else:
            result["overall_passed"] = result["execution_passed"]
        
        return result
    
    def check_all(self, root: Path, patterns: List[str], exclude: List[str], 
                  lint: bool = True) -> Dict[str, Any]:
        """Check all R scripts in project."""
        scripts = self.find_scripts(root, patterns, exclude)
        
        if not scripts:
            return {"scripts_found": 0, "results": []}
        
        results = []
        for script in scripts:
            result = self.check_script(script, lint)
            results.append(result)
        
        # Summary
        total = len(results)
        passed = sum(1 for r in results if r["overall_passed"])
        
        return {
            "root": str(root),
            "scripts_found": total,
            "results": results,
            "passed": passed,
            "failed": total - passed
        }