import cli
from ollama_client import ollama_client, llm
from security import validate_command, run_command
from explainer import CommandExplainer
import terminal_ui as ui

def cli_loop(model=None, explain_flag=False):
    
    ui.display_welcome()
    explainer = CommandExplainer(llm)

    while True:
        user_input = input("\nEnter English request (or 'exit'): ").strip()

        # Exit loop if user entered either exit or quit
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input:
            continue

        # Generate the user command by running client
        ui.display_status("Generating command")
        result = ollama_client(user_input)
        
        if not result.success:
            ui.display_error(result.error)
            continue
            
        ui.display_command(result.command)

        # Explain command if flag is set
        if explain_flag:
            ui.display_status("Explaining")
            exp = explainer.explain(result.command)
            if exp.success:
                ui.display_explanation(exp.summary, exp.breakdown, exp.warning)

        # Check security of command
        if not validate_command(result.command):
            ui.display_error("Command rejected by security policy.")
            continue

        # Execution of command if user selects yes
        confirm = input("\nRun command? (y/N): ").lower()
        if confirm == 'y':
            ui.display_status("Executing")
            stdout, stderr = run_command(result.command)
            if stdout: print(f"Output: {stdout}")
            if stderr: print(f"Error: {stderr}")

if __name__ == "__main__":
    # Hand control to the CLI module for flag parsing
    cli.run()