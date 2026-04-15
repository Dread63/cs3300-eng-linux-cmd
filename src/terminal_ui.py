from rich.console import Console

console = Console()

def display_welcome():
    console.print("[bold blue]Linux Command Assistant (Placeholder UI)[/bold blue]")

def display_command(command: str):
    console.print(f"\n[bold green]Suggested Command:[/bold green] {command}")

def display_explanation(summary: str, breakdown: list[str], warning: str):
    console.print(f"\n[blue]Summary:[/blue] {summary}")
    for item in breakdown:
        console.print(f" - {item}")
    if warning:
        console.print(f"[red]Warning:[/red] {warning}")

def display_error(msg: str):
    console.print(f"[red]Error:[/red] {msg}")

def display_status(msg: str):
    console.print(f"[italic]{msg}...[/italic]")