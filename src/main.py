# =========================
# HARD SILENCE MODE 
# =========================

# Comment this out if you are debugging 
import os
import sys
import warnings

# MUST be first: silence Python warnings
warnings.filterwarnings("ignore")

# HuggingFace + Transformers silence
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# llama.cpp silence
os.environ["GGML_LOG_LEVEL"] = "0"

# Prevent HF logging system from printing early
os.environ["HF_HUB_OFFLINE"] = "0"

# HARD PIPE STDERR 
class DevNull:
    def write(self, *_): pass
    def flush(self): pass

sys.stderr = DevNull()
sys.stdout = sys.stdout  # keep normal output

# =========================
# END OF HARD SILENCE MODE 
# =========================

import cli
from ollama_client import ollama_client, llm
from security import validate_command, run_command
from explainer import CommandExplainer
import terminal_ui as ui


def run_once(query, model=None, explain_flag=False):
    ui.display_welcome()
    explainer = CommandExplainer(llm)

    if not query:
        ui.display_error("No input provided.")
        return

    # Generate command
    ui.display_status("Generating command")
    result = ollama_client(query)

    if not result.success:
        ui.display_error(result.error)
        return

    ui.display_command(result.command)

    # Explain if flag set
    if explain_flag:
        ui.display_status("Explaining")
        exp = explainer.explain(result.command)
        if exp.success:
            ui.display_explanation(exp.summary, exp.breakdown, exp.warning)

    # Security check
    if not validate_command(result.command):
        ui.display_error("Command rejected by security policy.")
        return

    # Confirm execution
    confirm = input("\nRun command? (y/N): ").lower()
    if confirm == 'y':
        ui.display_status("Executing")
        stdout, stderr = run_command(result.command)
        if stdout:
            print(f"Output: {stdout}")
        if stderr:
            print(f"Error: {stderr}")


if __name__ == "__main__":
    cli.run()