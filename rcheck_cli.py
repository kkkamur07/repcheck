import os
import sys
import shlex
import subprocess # Main library for using the internal processes. 
from pathlib import Path
from time import perf_counter
from typing import List

# For UX and formatting the CLI Outputs. 
import typer
from rich.progress import track

app = typer.Typer(add_completion=False, help="Run R scripts via Rscript and report pass/fail.")

# Using python to find the scripts.
def find_scripts(root: Path, patterns: List[str], exclude: List[str]) -> List[Path]:
    found: List[Path] = []
    for dirpath, _, filenames in os.walk(root): # Main function os.walk() -> Generator. 
        for fn in filenames:
            p = Path(dirpath) / fn
            if not any(p.match(pat) for pat in patterns): # Finding the Rscripts. 
                continue
            if any(p.match(pat) for pat in exclude):
                continue
            found.append(p)
    return sorted(found)

# Running each R script individually.
def run_rscript(path: Path, timeout: int):
    cmd = ["Rscript", "--vanilla", str(path)]
    t0 = perf_counter()
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dur = perf_counter() - t0
        return {
            "path": str(path),
            "cmd": shlex.join(cmd),
            "code": res.returncode,
            "duration": round(dur, 3),
            "stdout": res.stdout,
            "stderr": res.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        dur = perf_counter() - t0
        return {
            "path": str(path),
            "cmd": shlex.join(cmd),
            "code": 124,
            "duration": round(dur, 3),
            "stdout": "",
            "stderr": f"Timed out after {timeout}s",
            "timed_out": True,
        }

@app.command("run-all")
def run_all(
    # New: -d/--directory to set the search root (kept as an option, no positional arg needed)
    directory: Path = typer.Option(
        Path("."),
        "--directory",
        "-d",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=False,
        readable=True,
        help="Root directory to search recursively",
    ),
    # Default to case-insensitive .R or .r via character class
    pattern: List[str] = typer.Option(
        ["**/*.[Rr]"],
        "--pattern",
        "-p",
        help="Glob(s) to include (repeatable). Defaults to '**/*.[Rr]'",
    ),
    exclude: List[str] = typer.Option(
        [],
        "--exclude",
        "-x",
        help="Glob(s) to exclude (repeatable), e.g., '*/ignored/*' or '*_draft.R'",
    ),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Per-script timeout (seconds)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress per-script logs; print summary only"),
):
    scripts = find_scripts(directory, pattern, exclude) #? First it is finding the scripts. 
    if not scripts:
        typer.echo("No scripts matched.")
        raise typer.Exit(code=0)

    results = []
    for p in track(scripts, description="Running R scripts..."):
        results.append(run_rscript(p, timeout)) #? Then running the scripts

    failures = 0
    if not quiet:
        for r in results:
            typer.echo("=== RUN SUMMARY ===")
            typer.echo(f"script: {r['path']}")
            typer.echo(f"cmd: {r['cmd']}")
            typer.echo(f"exit_code: {r['code']}  duration_s: {r['duration']}")
            if r["stdout"]:
                typer.echo("---- stdout ----")
                typer.echo(r["stdout"].rstrip("\n"))
            if r["stderr"]:
                typer.echo("---- stderr ----")
                typer.echo(r["stderr"].rstrip("\n"))
            typer.echo("")

    for r in results:
        if r["code"] != 0:
            failures += 1

    typer.echo("=== BATCH SUMMARY ===")
    typer.echo(f"root: {directory.resolve()}")
    typer.echo(f"scripts_found: {len(results)}")
    typer.echo(f"passed: {len(results) - failures}")
    typer.echo(f"failed: {failures}")

    raise typer.Exit(code=0 if failures == 0 else 1)

if __name__ == "__main__":
    app()
