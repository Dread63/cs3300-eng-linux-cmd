# =========================
# HARD SILENCE MODE 
# =========================


import os
import sys
import warnings

#for flags
from ollama_client import reset_config
from ollama_client import MODELS

# MUST be first: silence Python warnings
# warnings.filterwarnings("ignore")

# HARD PIPE STDERR 
class DevNull:
    def write(self, *_): pass
    def flush(self): pass

def apply_silence_mode():
    warnings.filterwarnings("ignore")

    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["GGML_LOG_LEVEL"] = "0"

    sys.stderr = DevNull()


#list_models flag
def list_models():
    print("\nAvailable Models:\n")
    
    for key, data in MODELS.items():
        print(f"{key}")
        print(data["description"])
        print()

# sys.stderr = DevNull()
sys.stdout = sys.stdout  # keep normal output

# =========================
# END OF HARD SILENCE MODE 
# =========================

import cli
from ollama_client import ollama_client, initialize
from security import validate_command, run_command
from explainer import CommandExplainer
from terminal_ui import TerminalUI

def cli_loop(
    query=None,
    model=None,
    explain_flag=False,
    debug_flag=False,
    reset_flag=False,
    list_models_flag=False
):
    if reset_flag:
        confirm = input("Reset local config? (y/N): ").strip().lower()

        if confirm == "y":
            if reset_config():
                print("Config reset successfully.")
            else:
                print("No config file found.")
        else:
            print("Reset cancelled.")

        return

    llm = initialize(model_flag=model)

    ui = TerminalUI()
    ui.show_banner()

    explainer = CommandExplainer(llm)

    first_iteration = True

    #debug mode flag implimentation
    if not debug_flag:
        apply_silence_mode()


    while True:

        #exit loop early if --list_model flag set
        if list_models_flag:
            list_models()
            return
        
        if first_iteration and query:
            user_input = query
            first_iteration = False
            print(f"\nInitial request: {user_input}")
        else:
            user_input = ui.get_query()

        # Exit loop if user entered either exit or quit
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input:
            continue

        # Generate the user command by running client
        result = ollama_client(user_input)
        
        if not result.success:
            ui.show_error(result.error)
            if debug_flag:
                print(f"DEBUG: The model actually said:\n{result.raw_output}")
            continue
            
        ui.show_command(result)

        # Explain command if flag is set
        if explain_flag:
            with ui.explaining_spinner():
                exp = explainer.explain(result.command)
            ui.show_explanation(exp)


        # Check security of command
        if not validate_command(result.command):
            ui.show_error("Command rejected by security policy.")
            continue

        # Execution of command if user selects yes
        confirm = input("\nRun command? (y/N): ").lower()
        if confirm == 'y':
            ui.executing_spinner()
            return_code = run_command(result.command)

            if return_code == 1:
                print("Command returned no results.")
            elif return_code != 0:
                print(f"Command Failed with return code: {return_code}")
    ui.show_goodbye()

if __name__ == "__main__":
    # Hand control to the CLI module for flag parsing
    cli.run()
