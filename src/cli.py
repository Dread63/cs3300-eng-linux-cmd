import typer
from typing import Optional

app = typer.Typer()

def run():
    app()

@app.command()
def main_command(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model choice"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Explain the command")
):
    # Import inside function to avoid circular dependency with main.py
    import main
    main.cli_loop(model=model, explain_flag=explain)
