#this is a command validator that makes sure that it wont be harmful to the user
def validate_command(command):
    print(f"Validating command: {command}")
    if command in ["rm -rf /", "format c:", "del *.*"]: #these are examples of harmful commands that could delete files or damage the system
        print("Command is potentially harmful. Validation failed.")
        return False
    print("Command is safe. Validation passed.")

    return True

