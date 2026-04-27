import subprocess
import os
import re

def validate_command(command: str) -> bool:
    """
    Checks if a command is in the blacklist of dangerous operations.
    """
    # Expanded blacklist based on team discussions
    harmful_commands = [
        "rm -rf /", 
        "rm -rf *", 
        "format c:", 
        "del *.*", 
        "mkfs", 
        "dd if=/dev/zero",
        ":(){ :|:& };:" # Fork bomb
    ]
    
    cmd_clean = command.strip().lower()
    
    for harmful in harmful_commands:
        if harmful in cmd_clean:
            return False
            
    return True

def determine_shell_state(command: str) -> bool:
    
    # TODO: Determine if there are more state changing commands we should be taking into account
    state_changing_commands = [
        "cd",
        "export",
        "alias",
        "set",
        "unset",
    ]

    cmd_clean = command.strip().lower()

    for cmd in state_changing_commands:
        if re.search(r'\b' + re.escape(cmd) + r'\b', cmd_clean):
            return True

    return False

def run_command(command: str):
    """
    Executes the command in the shell and returns the return code.
    """
    
    state_changing = determine_shell_state(command)
    
    if state_changing:
        if command.startswith("cd "):
            try:
                # Set path = the first occurances of cd removed from the command (hopefully leaving just the path)
                path = command.replace("cd ", "", 1).strip()
                
                # Change directory of current script to proposed directory from model
                os.chdir(os.path.expanduser(path))
                return 0
            except Exception as e:
                print(f"Error changing directories: {e}")
                return 1
        
        if command.startswith("export ") or command.startswith("set "):
            try:
                parts = command.split(None, 1)[1].split("=", 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]
                else:
                    print(f"Could not parse variable assignment: {command}")
                    return 1
            except Exception as e:
                print(f"Error setting variable: {e}")
                return 1

        if command.startswith("unset "):
            try:
                var_name = command.split()[1]
                os.environ.pop(var_name, None)
            except Exception as e:
                print(f"Error unsetting variable: {e}")
                return 1
            
        if command.startswith("alias "):
            print("Alias not supported by utility, you must complete this action in your terminal manually")
            
        
        return 0

    try:
        # Use bash on Linux/Mac, default shell on Windows
        executable = '/bin/bash' if os.name != 'nt' else None
        
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            text=True,
            executable=executable
        )
        return result.returncode
    except Exception as e:
        print(f"Command execution failed: {e}")
        return 1
