import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

from repcheck.checkers import RScriptChecker
from repcheck.llm_handler import OllamaHandler
from repcheck.dependency_resolver import RScriptOrderResolver

app = typer.Typer(help="R Script Checker")
console = Console()

@app.command()
def check(
    directory: Path = typer.Option(Path("."), "--dir", "-d"),
    pattern: List[str] = typer.Option(["**/*.[Rr]"], "--pattern", "-p"),
    exclude: List[str] = typer.Option([], "--exclude", "-x"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip AI analysis")
):
    """Check R scripts and show comprehensive results."""
    
    # Initialize components
    checker = RScriptChecker()
    resolver = RScriptOrderResolver()
    llm = OllamaHandler() if not no_llm else None
    
    # Find scripts
    scripts = checker.find_scripts(directory, pattern, exclude)
    if not scripts:
        console.print("[yellow]No R scripts found[/yellow]")
        return
    
    # Get execution order
    order_result = resolver.resolve_execution_order(scripts)
    
    # Show execution order first
    console.print("[bold blue]📋 Execution Order:[/bold blue]")
    if order_result["has_circular_dependency"]:
        console.print("[red]❌ Circular dependency detected![/red]")
        console.print("Scripts found but cannot determine safe execution order:")
        for script in scripts:
            console.print(f"  • {script.name}")
        execution_order = [str(s) for s in scripts]  # Use original order as fallback
    else:
        execution_order = order_result["execution_order"]
        for i, script_path in enumerate(execution_order, 1):
            console.print(f"  {i}. [cyan]{Path(script_path).name}[/cyan]")
    
    console.print()
    
    # Check all scripts in order
    console.print("[bold blue]🔍 Running Checks...[/bold blue]")
    results = []
    
    for script_path in track(execution_order, description="Checking scripts..."):
        result = checker.check_script(Path(script_path))
        result["execution_order"] = execution_order.index(script_path) + 1
        results.append(result)
    
    # Create comprehensive results table
    table = Table(title="R Script Analysis Results")
    table.add_column("Order", justify="center", style="cyan")
    table.add_column("Script", style="bold")
    table.add_column("Lint", justify="center")
    table.add_column("Execute", justify="center") 
    table.add_column("Duration", justify="center")
    table.add_column("Status", justify="center")
    
    for result in results:
        script_name = Path(result["path"]).name
        order_num = str(result["execution_order"])
        
        # Status indicators
        lint_status = "✅" if result.get("lint_passed", True) else "❌"
        exec_status = "✅" if result["execution_passed"] else "❌"
        duration = f"{result.get('duration', 0):.2f}s"
        overall_status = "✅ PASS" if result["overall_passed"] else "❌ FAIL"
        
        # Color coding for overall status
        if result["overall_passed"]:
            status_style = "[green]✅ PASS[/green]"
        else:
            status_style = "[red]❌ FAIL[/red]"
        
        table.add_row(
            order_num,
            script_name,
            lint_status,
            exec_status,
            duration,
            status_style
        )
    
    console.print(table)
    
    # Show detailed errors and AI analysis
    failed_results = [r for r in results if not r["overall_passed"]]
    if failed_results:
        console.print(f"\n[bold red]❌ Failed Scripts Details ({len(failed_results)}):[/bold red]")
        
        for result in failed_results:
            script_name = Path(result["path"]).name
            console.print(f"\n[bold red]🔴 {script_name}[/bold red]")
            
            # Lint issues
            if not result.get("lint_passed", True):
                lint_output = result.get("lint_output", "No details available")
                console.print(f"[yellow]📝 Lint Issues:[/yellow]")
                console.print(f"   {lint_output[:200]}...")
            
            # Execution errors
            if not result["execution_passed"]:
                error = result.get("stderr", "No error details")
                console.print(f"[red]💥 Execution Error:[/red]")
                console.print(f"   {error[:200]}...")
                
                # AI Analysis
                if llm and llm.is_available():
                    with console.status("🤖 Getting AI analysis..."):
                        explanation = llm.analyze_error(result["path"], error)
                    
                    if explanation:
                        panel = Panel(
                            explanation,
                            title="🤖 AI Analysis",
                            border_style="blue",
                            padding=(1, 2)
                        )
                        console.print(panel)
    
    # Summary
    total = len(results)
    passed = len([r for r in results if r["overall_passed"]])
    failed = total - passed
    
    console.print(f"\n[bold]📊 Summary:[/bold]")
    console.print(f"   Total Scripts: {total}")
    console.print(f"   ✅ Passed: [green]{passed}[/green]")
    console.print(f"   ❌ Failed: [red]{failed}[/red]")
    console.print(f"   Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        raise typer.Exit(1)

@app.command()
def order(
    directory: Path = typer.Option(Path("."), "--dir", "-d"),
    pattern: List[str] = typer.Option(["**/*.[Rr]"], "--pattern", "-p")
):
    """Show script execution order only."""
    
    checker = RScriptChecker()
    resolver = RScriptOrderResolver()
    
    scripts = checker.find_scripts(directory, pattern, [])
    if not scripts:
        console.print("[yellow]No R scripts found[/yellow]")
        return
    
    order_result = resolver.resolve_execution_order(scripts)
    
    # Create order table
    table = Table(title="Script Execution Order")
    table.add_column("Order", justify="center", style="cyan")
    table.add_column("Script", style="bold")
    table.add_column("Dependencies", style="dim")
    
    if order_result["has_circular_dependency"]:
        console.print("[red]❌ Circular dependency detected![/red]")
        for i, script in enumerate(scripts, 1):
            table.add_row(str(i), script.name, "[red]Circular![/red]")
    else:
        dep_graph = order_result["dependency_graph"]
        for i, script_path in enumerate(order_result["execution_order"], 1):
            script_name = Path(script_path).name
            deps = dep_graph.get(script_path, [])
            
            if deps:
                dep_names = [Path(d).name for d in deps]
                dep_text = ", ".join(dep_names)
            else:
                dep_text = "None"
            
            table.add_row(str(i), script_name, dep_text)
    
    console.print(table)

if __name__ == "__main__":
    app()