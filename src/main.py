from ollama_client import ollama_client
from cli import cli
from command_runner import run_command
from command_validator import validate_command
from prompt_builder import build_prompt
from response_parser import parse_response

def main():

    print("Type 'exit' or 'quit' to close the program.\n")

    while True:

        # Get user input
        user_input = cli()

        if user_input.lower() in ['exit', 'quit']:
            print("Exiting...\n")
            break
            
        if not user_input.strip():
            continue

        # Pass input to prompt builder (currently does nothing)
        prompt = build_prompt(user_input)

        # Pass prompt to ollama client for processing
        print(f"\nProcessing request...")
        # Pass prompt to ollama client
        llm_output = ollama_client(prompt)

        # Parse llm response in order to validate cmd
        parsed_cmd = parse_response(llm_output)

        print(f"\nSuggested Command: {parsed_cmd}")
        print("Verifing command saftery...\n")

        # Validate llm output with user input
        is_safe = validate_command(parsed_cmd)

        if is_safe:

            user_confirmation = input(f"Would you like to run this command? (y/n): ").strip().lower()
            
            if user_confirmation == 'y':

                print(f"Executing: {parsed_cmd}")

                # Store standard output and standard error for printing to shell
                stdout, stderr = run_command(parsed_cmd, 'y')
                
                if stdout:
                    print(f"\nOutput:\n{stdout}")
                if stderr:
                    print(f"\nError:\n{stderr}")
            else:
                print("Command cancled by user")
        else:
            print("Command is potentially harmful and will not be executed")

if __name__ == "__main__":
    main()
