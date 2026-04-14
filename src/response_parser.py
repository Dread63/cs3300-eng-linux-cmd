# Parse response only used to hide internal functionality of clean command
def parse_response(llm_output):

    return clean_command(llm_output)

def clean_command(raw_command):
    # Remove backticks
    command = raw_command.strip()
    if command.startswith('`') and command.endswith('`'):
        command = command[1:-1]
    # Remove single quotes if they wrap the whole command
    if command.startswith("'") and command.endswith("'"):
        command = command[1:-1]
    # Remove double quotes if they wrap the whole command
    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]
    return command