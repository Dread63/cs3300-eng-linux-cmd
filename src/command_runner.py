import subprocess

# Assuming user has already agreed to running command
def run_command(command, y_n):

    if y_n == 'y':
        try:
            cmd_output = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash')
            return cmd_output.stdout, cmd_output.stderr
        except Exception as e:
            print(e)
    else:
        return None, None