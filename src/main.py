# =========================
# HARD SILENCE MODE
# =========================
import os
import sys
import warnings

warnings.filterwarnings("ignore")

os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["GGML_LOG_LEVEL"] = "0"
os.environ["HF_HUB_OFFLINE"] = "0"

class DevNull:
    def write(self, *_): pass
    def flush(self): pass

sys.stderr = DevNull()
# =========================
# END OF HARD SILENCE MODE
# =========================

import cli
from ollama_client import ollama_client, initialize
from security import validate_command, run_command
from explainer import CommandExplainer
from terminal_ui import TerminalUI

def cli_loop(query=None, model=None, explain_flag=False):

    llm = initialize(model_flag=model)

    ui = TerminalUI()
    ui.show_banner()

    explainer = CommandExplainer(llm)

    first_iteration = True

    while True:
        if first_iteration and query:
            user_input = query
            first_iteration = False
            ui._line("INPUT", user_input)
        else:
            user_input = ui.get_query()

        if user_input.lower() in ['exit', 'quit']:
            break

        if not user_input:
            continue

        with ui.translating_spinner():
            result = ollama_client(user_input)

        if not result.success:
            ui.show_error(result.error)
            continue

        ui.show_command(result)

        if explain_flag:
            with ui.explaining_spinner():
                exp = explainer.explain(result.command)
            if exp.success:
                ui.show_explanation(exp)

        if not validate_command(result.command):
            ui.show_error("Command rejected by security policy.")
            continue

        confirm = input("\nRun command? (y/N): ").lower()
        if confirm == 'y':
            with ui.executing_spinner():
                return_code = run_command(result.command)

            if return_code == 1:
                print("Command returned no results.")
            elif return_code != 0:
                print(f"Command Failed with return code: {return_code}")
    ui.show_goodbye()

if __name__ == "__main__":
    cli.run()
