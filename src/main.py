from ollama_client import ollama_client
from cli import cli
from command_runner import run_command
from command_validator import validate_command
from prompt_builder import build_prompt
from response_parser import parse_response

def main():

    while True:

        # Get user input
        user_input = cli()

        # Pass input to prompt builder
        prompt = build_prompt(user_input)

        # Pass prompt to ollama client
        llm_output = ollama_client(prompt)

        # Parse llm response in order to validate cmd
        parsed_cmd = parse_response(llm_output)

        # Validate llm output with user input
        user_run_choice = validate_command(parsed_cmd)

        # Run command based on user entry
        cmd_output = run_command(parsed_cmd, user_run_choice)

        #