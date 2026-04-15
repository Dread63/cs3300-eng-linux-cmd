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

def run_command(command: str):
    """
    Executes the command in the shell and returns (stdout, stderr).
    """
    try:
        # Use bash on Linux/Mac, default shell on Windows
        executable = '/bin/bash' if os.name != 'nt' else None
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            executable=executable
        )
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)
