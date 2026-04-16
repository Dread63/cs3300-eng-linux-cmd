import subprocess
import os

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

# TODO: Implement shell state handling
# Used to handle shell changing commands such as cd, alias, etc
# Return True if state changing, flase if not
def determine_shell_state(command: str) -> bool:
    
    # TODO: Determine if there are more state changing commands we should be taking into account
    state_changing_commands = [
        "cd",
        "export",
        "alials",
        "set",
        "unset",
    ]
    
    cmd_clean = command.strip().lower()
    
    for cmd in state_changing_commands:
        if cmd in cmd_clean:
            return True
        
    return False

def run_command(command: str):
    """
    Executes the command in the shell and returns (stdout, stderr).
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
        
        return 0
    #TODO: Implement logic for other state changing commands
    
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
        return None, str(e)
