import typer
from typing import Optional

app = typer.Typer()

def run():
    app()


@app.command()
def main_command(
    query: Optional[str] = typer.Argument(None, help="English request to convert into a command"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model choice"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Explain the command"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Show full errors and logs"),
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset config.json"),
    list_models: bool = typer.Option(False, "--list-models", "-lm", help="List available models")
):
    import main
    main.cli_loop(
        query=query,
        model=model,
        explain_flag=explain,
        debug_flag=debug,
        reset_flag=reset,
        list_models_flag=list_models
    )