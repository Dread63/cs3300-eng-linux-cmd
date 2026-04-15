from llama_cpp import Llama
import os
import json
import platform # from translator.py
import re       # from translator.py
from dataclasses import dataclass # from translator.py

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

# Model initialization (User's Style)
llm = Llama.from_pretrained(
    repo_id="bartowski/Qwen2.5-7B-Instruct-GGUF",
    filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    chat_format="chatml",
    verbose=False
)

# Define LLM identity (Merged OS context and rules)
os_context = _build_os_context()
llm_identity = (
    f"You are a Linux expert on {os_context}. "
    "Given an English description, output a single safe shell command.\n"
    "Reply using EXACTLY these three lines:\n"
    "COMMAND: <the shell command>\n"
    "CONFIDENCE: high|medium|low\n"
    "WARNING: <danger note or 'none'>\n\n"
    "Rules:\n"
    "- Output only the three lines above, nothing else.\n"
    "- Never use sudo unless the user explicitly asks.\n"
    "- Prefer safe flags (e.g. -i for confirmation on rm)."
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

def ollama_client(llm_input) -> TranslationResult:
    session = ChatSession(chat_history_file="src/chat_history.json")
    session.add_msg_history("user", llm_input)

    messages = [{"role": "system", "content": llm_identity}] + session.history

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
