def parse_response(llm_output):

    raw_command = llm_output['message']['content']
    return clean_command(raw_command)

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