import typer
from typing import Optional

app = typer.Typer()

def run():
    app()


@app.command()
def main_command(
    query: Optional[str] = typer.Argument(None, help="English request to convert into a command"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model choice"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Explain the command")
):
    import main
    main.cli_loop(query=query, model=model, explain_flag=explain)
