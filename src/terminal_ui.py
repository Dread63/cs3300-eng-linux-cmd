"""
terminal_ui.py

1. Shows a banner
2. Takes user input
3. Displays command info
4. Explains what it will do
5. Uses spinners during processing
"""
from contextlib import contextmanager
from rich.console import Console


class TerminalUI:
    def __init__(self):
        self.c = Console()
        self.div = "  " + "─" * 40

    # helpers
    def _line(self, label: str = "", value: str = "", style="bright_black"):
        if label:
            self.c.print(f"  [{style}]{label:<8}[/] {value}")
        else:
            self.c.print(f"  {value}")

    def _divider(self):
        self.c.print(self.div, style="bright_black")

    # Startup
    def show_banner(self):
        self.c.print()
        self.c.print(
            """[white]
   ███████╗███╗   ██╗      ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
   ██╔════╝████╗  ██║      ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
   █████╗  ██╔██╗ ██║█████╗██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝ 
   ██╔══╝  ██║╚██╗██║╚════╝██║     ██║██║╚██╗██║██║   ██║ ██╔██╗ 
   ███████╗██║ ╚████║      ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
   ╚══════╝╚═╝  ╚═══╝      ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝
   [/white]"""
        )
        self._divider()
        self._line("", "Type a command. exit to quit.", "dim")
        self.c.print()

    # Input
    def get_query(self) -> str:
        self.c.print()
        return self.c.input("  [bright_black]INPUT   [/]").strip()

    # Command display
    def show_command(self, t):
        color = {
            "high": "bold green",
            "medium": "bold yellow",
            "low": "bold red",
        }.get(t.confidence, "white")

        self.c.print()
        self._divider()
        self._line("COMMAND", t.command)
        self._line("CONF", f"[{color}]{t.confidence.upper()}[/]")

        if t.warning:
            self._line("WARNING", f"[yellow]{t.warning}[/]")

        self._divider()

    # Explanation
    def show_explanation(self, e):
        if not e.success:
            self._line("", f"[dim]{e.error}[/]")
            return

        self._line("SUMMARY", f"[dim]{e.summary}[/]")
        self.c.print()

        for b in e.breakdown:
            if ":" in b:
                k, _, v = b.partition(":")
                self._line("", f"[white]{k.strip():<10}[/][dim]{v.strip()}[/]")
            else:
                self._line("", f"[dim]{b}[/]")

        if e.warning:
            self.c.print()
            self._line("WARNING", f"[yellow]{e.warning}[/]")

        self._divider()

    # Errors + Exit
    def show_error(self, msg: str):
        self.c.print()
        self._line("ERROR", f"[bold red]{msg}[/]")
        self._divider()

    def show_goodbye(self):
        self.c.print()
        self._divider()
        self.c.print(
                """[dim]
             ██████╗  ██████╗  ██████╗ ██████╗     ██████╗ ██╗   ██╗███████╗
            ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗    ██╔══██╗╚██╗ ██╔╝██╔════╝
            ██║  ███╗██║   ██║██║   ██║██║  ██║    ██████╔╝ ╚████╔╝ █████╗  
            ██║   ██║██║   ██║██║   ██║██║  ██║    ██╔══██╗  ╚██╔╝  ██╔══╝  
            ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝    ██████╔╝   ██║   ███████╗
            ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝     ╚═════╝    ╚═╝   ╚══════╝
                    [/dim]"""
                )
        self._divider()
        self.c.print()

    # Spinners
    @contextmanager
    def _spinner(self, label: str, color="white"):
        with self.c.status(
            f"  [bright_black]{label}[/]",
            spinner="dots",
            spinner_style=color,
        ):
            yield

    def translating_spinner(self):
        return self._spinner("THINKING")

    def explaining_spinner(self):
        return self._spinner("EXPLAINING")

    def executing_spinner(self):
        return self._spinner("RUNNING", "green")