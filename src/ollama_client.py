from llama_cpp import Llama
import os
import getpass # used to gather model context
from datetime import datetime # used to gather model context
import json
import platform # from translator.py
from dataclasses import dataclass # from translator.py
import requests
from clint.textui import progress

#MODEL_DIR = os.path.expanduser("~/.local/share/eng-linux-cmd/")
MODEL_NAME = "qwen2.5-1.5b-instruct-q5_k_m.gguf"
MODEL_DOWNLOAD_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf"
#MODEL_FULL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
MAX_MSG_RETENTION = 10

#TODO: Implement error handling (try/catch blocks)

# From translator.py
@dataclass
class TranslationResult:
    command: str       # The Linux command
    confidence: str    # high/medium/low
    raw_output: str    # Raw model text (for debugging)
    success: bool
    error: str = ""
    warning: str = ""

def _build_os_context() -> str:
    """
    Grab the current OS/distro so the model knows what kind of
    Linux system it's writing commands for.
    """
    try:
        if hasattr(platform, 'freedesktop_os_release'):
            info = platform.freedesktop_os_release()
            return info.get("PRETTY_NAME", platform.system())
        return platform.system()
    except (AttributeError, OSError):
        return platform.system()
    
# Used to gather information on current runtime such as current directory, user information, and date/time
def build_runtime_context() -> str:

  
    # Get basics on user information and current directory
    current_dir = os.getcwd()
    user = getpass.getuser()
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # List files in current directory (max of 20 for token usage preservation)
    try:
        files = os.listdir(current_dir)[:20]
        files_list = ", ".join(files)
    except OSError:
        files_list = "None"

    runtime_context = (
        f"CURRENT_USER: {user}\n"
        f"CURRENT_DIRECTORY: {current_dir}\n"
        f"FILES_IN_DIR: {files_list}\n"
        f"SYSTEM_TIME: {date_time}"
    )

    return runtime_context, user

def _parse_response(raw: str) -> TranslationResult:
    """Parse the structured model output into a TranslationResult."""
    command = confidence = warning = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith("COMMAND:"):
            command = line.split(":", 1)[1].strip().strip("`")
        elif line.upper().startswith("CONFIDENCE:"):
            confidence = line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("WARNING:"):
            raw_warn = line.split(":", 1)[1].strip()
            if raw_warn.lower() not in {"none", "n/a", "none.", ""}:
                warning = raw_warn

    if not command:
        # Fallback: try to grab first code-looking line
        for line in raw.splitlines():
            line = line.strip().strip("`")
            if line and not line[0].isupper():
                command = line
                break

    if not command:
        return TranslationResult("", "low", raw, False, "Could not extract a command.")

    return TranslationResult(
        command=command,
        confidence=confidence or "medium",
        raw_output=raw,
        success=True,
        warning=warning,
    )
# --- End of translator.py logic ---

# TODO: Fix library searching on macos
def get_model_dir():
    system_name = platform.system()

    if system_name == "Darwin":
        return os.path.expanduser("~/Library/Application Support/eng-linux-cmd")
    elif system_name == "Linux":
        return os.path.expanduser("~/.local/share/eng-linux-cmd")
    else:
        raise OSError(f"Unsupported operating system: {system_name}")

MODEL_DIR = get_model_dir()
MODEL_FULL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

# Download model on first run if file doesn't exist
if not os.path.exists(MODEL_FULL_PATH):
    
    print("Model not installed. Downloading now...")
    print(f"Installing {MODEL_NAME}:")

    os.makedirs(MODEL_DIR, exist_ok=True)

    # Stream file download so we can write each chunk as they come through
    with requests.get(MODEL_DOWNLOAD_URL, stream=True) as r:

        # Used for error checking
        r.raise_for_status()

        with open(MODEL_FULL_PATH, 'wb') as f:

            total_file_length = int(r.headers.get('content-length'))

            # Download model in 8192 byte chunks and display progress bar (from clint library)
            for chunk in progress.bar(r.iter_content(chunk_size=8192), expected_size=(total_file_length/8192 + 1)):
                f.write(chunk)
                f.flush()

# Model initialization (User's Style)
llm = Llama(
    model_path=MODEL_FULL_PATH,
    n_ctx = 2048,
    n_threads = 4,
    chat_format="chatml",
    verbose=False
)

class ChatSession:
    def __init__(self, chat_history_file="src/chat_history.json"):
        self.chat_history_file = chat_history_file
        self.history = self.load_msg_history()

    def load_msg_history(self):
        if os.path.exists(self.chat_history_file):
            try:
                with open(self.chat_history_file, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_msg_history(self):
        try:
            with open(self.chat_history_file, "w") as file:
                json.dump(self.history, file, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")

    def add_msg_history(self, role, msg_content):
        self.history.append({"role": role, "content": msg_content})
        self.save_msg_history()

    # Remove oldest message if history reaches greater than 10 messages in order to remain in 2048 context window
    # TODO: Update this to prune based on token size not number of messages
    def prune_msg_history(self):

        if len(self.history) > MAX_MSG_RETENTION:
            self.history = self.history[-MAX_MSG_RETENTION:]
        self.save_msg_history()

# Used to build message using context helper functions and message history, then pass to the model to process
def ollama_client(llm_input) -> TranslationResult:
    
    runtime_state, current_user = build_runtime_context()
    os_info = _build_os_context()

    # Define LLM identity (Merged OS context and rules)
    # TODO: Fix confidence level within prompt, currently the confidence level always comes out as "high"
    llm_identity = (
        f"You are a Linux expert on {os_info}.\n"
        f"--- SYSTEM STATE ---\n{runtime_state}\n\n"

        "--- EXAMPLE ---\n"
        "User: show my home files with an absolute path\n"
        "Assistant:\n"
        f"COMMAND: ls /home/{current_user}/\n"
        "CONFIDENCE: high\n"
        "WARNING: none\n\n"

        "--- RULES ---\n"
        "1. Output EXACTLY three lines (COMMAND, CONFIDENCE, WARNING).\n"
        "2. Use the REAL paths and usernames from the SYSTEM STATE above.\n"
        "3. Never use generic placeholders like '/username'.\n"
        "4. Never use sudo unless explicitly requested.\n"
        "5. Prefer safe flags (e.g. -i for rm).\n\n"

        "--- TASK ---\n"
        "Now provide the command for the following request:"
    )

    session = ChatSession(chat_history_file="src/chat_history.json")
    session.add_msg_history("user", llm_input)

    messages = [{"role": "system", "content": llm_identity}] + session.history

    # After adding users message to history, cut the oldest off
    session.prune_msg_history()

    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.15 # From translator.py for precision
    )

    llm_reply = response["choices"][0]["message"]["content"]
    
    # Parse the response using the methodical logic from translator.py
    result = _parse_response(llm_reply)
    
    # Still add the full reply to history for context
    session.add_msg_history("assistant", llm_reply)

    return result