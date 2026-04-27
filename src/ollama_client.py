from llama_cpp import Llama
import os
import sys
import getpass # used to gather model context
from datetime import datetime # used to gather model context
import json
import platform # from translator.py
from dataclasses import dataclass # from translator.py
import requests
from clint.textui import progress

MAX_MSG_RETENTION = 20
MAX_HISTORY_TOKENS = 500  # tune this to adjust how much chat history the model sees

MODELS = {
    "qwen2.5-0.5b": {
        "name": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf?download=true",
        "description": (
            "────────────────────────────────────────\n"
            "MODEL     Qwen2.5-0.5B\n"
            "TYPE      Instruct / Lightweight\n"
            "FORMAT    GGUF (Q4_K_M quantized)\n"
            "SIZE      ~0.49B params (0.36B effective)\n"
            "MEMORY    ~0.5–1GB RAM\n"
            "\n"
            "CONTEXT   32K tokens\n"
            "GEN       up to 8K tokens\n"
            "\n"
            "STRENGTH  Fast inference\n"
            "          Strong instruction following\n"
            "          Reliable structured outputs\n"
            "          Prompt-robust behavior\n"
            "\n"
            "LIMIT     Weaker reasoning depth\n"
            "          Limited world knowledge\n"
            "\n"
            "USECASE   Edge devices\n"
            "          CLI tools / agents\n"
            "          Low-latency pipelines\n"
            "────────────────────────────────────────"
        ),
    },

    "qwen2.5-1.5b": {
        "name": "qwen2.5-1.5b-instruct-q5_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf",
        "description": (
            "────────────────────────────────────────\n"
            "MODEL     Qwen2.5-1.5B\n"
            "TYPE      Instruct / General Purpose\n"
            "FORMAT    GGUF (Q5_K_M quantized)\n"
            "SIZE      1.5B params\n"
            "MEMORY    ~1.5–3GB RAM\n"
            "\n"
            "CONTEXT   up to 128K tokens\n"
            "GEN       up to 8K tokens\n"
            "\n"
            "STRENGTH  Reasoning & logic\n"
            "          Coding assistance\n"
            "          Math capabilities\n"
            "          Long-context handling\n"
            "          Structured data (tables/json)\n"
            "\n"
            "LANG      29+ supported\n"
            "          EN, ZH, ES, FR, DE, JP, KR, AR...\n"
            "\n"
            "LIMIT     Slower than sub-1B models\n"
            "          Moderate RAM requirement\n"
            "\n"
            "USECASE   Chatbots\n"
            "          Agents / workflows\n"
            "          Multi-language systems\n"
            "────────────────────────────────────────"
        ),
    },

    "gemma-2b": {
        "name": "gemma-2b-it.gguf",
        "url": "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf?download=true",
        "description": (
            "────────────────────────────────────────\n"
            "MODEL     Gemma 2B\n"
            "TYPE      Instruction-tuned / Decoder-only\n"
            "ORIGIN    Google (Gemini research)\n"
            "FORMAT    GGUF (Q4_K_M quantized)\n"
            "SIZE      ~2B params\n"
            "MEMORY    ~2–4GB RAM\n"
            "\n"
            "CAPABLE   Question answering\n"
            "          Summarization\n"
            "          General reasoning\n"
            "          Clean text generation\n"
            "\n"
            "ADVANT    Small + efficient\n"
            "          Open weights\n"
            "          Easy local deployment\n"
            "\n"
            "LIMIT     Less tuned for tools/agents\n"
            "          Narrower multilingual support\n"
            "\n"
            "USECASE   Local assistants\n"
            "          Offline AI\n"
            "          Personal workflows\n"
            "────────────────────────────────────────"
        ),
    },
    
    "deepseek-coder-1.3b": {
    "name": "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
    "url": "https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf?download=true",
    "description": (
        "────────────────────────────────────────\n"
        "MODEL     DeepSeek Coder 1.3B\n"
        "TYPE      Code-specialized / Instruct\n"
        "FORMAT    GGUF (Q4_K_M quantized)\n"
        "SIZE      1.3B params\n"
        "MEMORY    ~1.5–3GB RAM\n"
        "\n"
        "CONTEXT   16K tokens\n"
        "GEN       Code + text output\n"
        "\n"
        "TRAINING  2T tokens total\n"
        "          87% code / 13% natural language\n"
        "          +2B instruction tuning\n"
        "\n"
        "STRENGTH  Code generation\n"
        "          Completion & infilling\n"
        "          Multi-language support\n"
        "          Project-level reasoning\n"
        "\n"
        "BENCH     HumanEval • MBPP • APPS • DS-1000\n"
        "\n"
        "LIMIT     Weaker general chat\n"
        "          Less natural conversation\n"
        "\n"
        "USECASE   Dev tools\n"
        "          Code agents\n"
        "          IDE integration\n"
        "────────────────────────────────────────"
        ),
    },
}

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
def _build_runtime_context() -> tuple[str, str]:

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

# Find installation directory of model based on system OS
def _get_model_dir():
    system_name = platform.system()

    if system_name == "Darwin":
        return os.path.expanduser("~/Library/Application Support/eng-linux-cmd")
    elif system_name == "Linux":
        return os.path.expanduser("~/.local/share/eng-linux-cmd")
    else:
        # WINDOWS NOT CURRENTLY SUPPORTED
        raise OSError(f"Unsupported operating system: {system_name}")

# Get set model directory before creating full path
try:
    MODEL_DIR = _get_model_dir()
except OSError as e:
    print(f"Error: {e}")
    sys.exit(1)

CONFIG_PATH = os.path.join(MODEL_DIR, "config.json")
CHAT_HISTORY_PATH = os.path.join(MODEL_DIR, "chat_history.json")

# Module-level globals set by initialize()
_llm = None
_session = None

def load_config() -> str | None:

    if os.path.exists(CONFIG_PATH): 
        try:
            with open(CONFIG_PATH, "r") as config_file:
                return json.load(config_file).get("model")
        except (json.JSONDecodeError, IOError):
                return None
    else:
        return None

def save_config(model_key: str):

    try:
        with open(CONFIG_PATH, "w") as config_file:
            json.dump({"model": model_key}, config_file, indent=4)
    except IOError as e:
        print(f"Failed to save config data {e}")
   
def prompt_model_selection() -> str:

    model_keys = list(MODELS.keys())

    print("-----------MODELS----------")
    for i, key in enumerate(model_keys, 1):
        print(f"{i}. {key}\n{MODELS[key]['description']}\n")
    print(f"Enter a number (1-{len(model_keys)}) or model name to select.")

    while True:
        user_input = input("\nSelect a Model: ").strip()

        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(model_keys):
                return model_keys[index]
            print(f"Invalid number. Please enter 1-{len(model_keys)}.")
        elif user_input in MODELS:
            return user_input
        else:
            print(f"Invalid selection '{user_input}'. Enter a number 1-{len(model_keys)} or a model name.")
    
def resolve_model(model_flag: str | None) -> str:

    if model_flag:
        if model_flag not in MODELS:
            print(f"Unknown model '{model_flag}'. Available: {', '.join(MODELS.keys())}")
            sys.exit(1)
        save_config(model_flag)
        return model_flag

    saved = load_config()
    if saved and saved in MODELS:
        return saved

    key = prompt_model_selection()
    save_config(key)
    return key

def download_model(model_full_path: str, model_key: str):
    
    if not os.path.exists(model_full_path):
    
        print("Model not installed. Downloading now...")
        print(f"Installing: {MODELS[model_key]['name']}")

        os.makedirs(MODEL_DIR, exist_ok=True)

        try:
            # Stream file download so we can write each chunk as they come through
            with requests.get(MODELS[model_key]['url'], stream=True) as r:

                # Used for error checking
                r.raise_for_status()

                with open(model_full_path, 'wb') as f:

                    total_file_length = int(r.headers.get('content-length', 0))

                    # Download model in 8192 byte chunks and display progress bar (from clint library)
                    for chunk in progress.bar(r.iter_content(chunk_size=8192), expected_size=(total_file_length/8192 + 1)):
                        f.write(chunk)
                        f.flush()

        except (requests.RequestException, OSError) as e:
            if os.path.exists(model_full_path):
                # Remove the path if an error occured to ensure download on next run
                os.remove(model_full_path)
            print(f"Download failed: {e}")
            sys.exit(1)

def initialize(model_flag: str | None = None) -> Llama:

    """ Used to instantiate the model object, download the selected model, and instantiate a chat session
    _llm -> Llama : model object
    _session -> ChatSession : class to store chat history data for maintained context (passed to model on each request)
    """

    global _llm, _session

    model_key = resolve_model(model_flag)
    model_full_path = os.path.join(MODEL_DIR, MODELS[model_key]["name"])

    download_model(model_full_path, model_key)

    try:
        _llm = Llama(
            model_path=model_full_path,
            n_ctx=2048,
            n_threads=4,
            chat_format="chatml",
            verbose=False
        )
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)

    _session = ChatSession(chat_history_file=CHAT_HISTORY_PATH)
    return _llm

class ChatSession:
    def __init__(self, chat_history_file=CHAT_HISTORY_PATH):
        self.chat_history_file = chat_history_file
        self.history = self.load_msg_history()
        self.total_tokens = 0

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

    def count_history_tokens(self):
        self.total_tokens = 0

        for json_entry in self.history:
            try:
                tokens = _llm.tokenize(json_entry["content"].encode("utf-8"))
            except (UnicodeEncodeError, ValueError):
                tokens = []
            self.total_tokens += len(tokens)

    # Prune oldest message data from history if exceeding max token threshold. Fallback for max msg retention
    def prune_msg_history(self):

        self.count_history_tokens()

        while self.total_tokens > MAX_HISTORY_TOKENS:

            self.history.pop(0)
            self.count_history_tokens()

        if len(self.history) > MAX_MSG_RETENTION:
            self.history = self.history[-MAX_MSG_RETENTION:]
            self.count_history_tokens()
        self.save_msg_history()

# Used to build message using context helper functions and message history, then pass to the model to process
def ollama_client(user_input) -> TranslationResult:

    runtime_state, current_user = _build_runtime_context()
    os_info = _build_os_context()

    system_prompt = (
        f"You are a Linux expert on {os_info}.\n"
        f"--- SYSTEM STATE ---\n{runtime_state}\n\n"

        "--- EXAMPLES ---\n"
        "User: show my home files with an absolute path\n"
        "Assistant:\n"
        f"COMMAND: ls /home/{current_user}/\n"
        "CONFIDENCE: high\n"
        "WARNING: none\n\n"

        "User: find large log files somewhere on the system\n"
        "Assistant:\n"
        "COMMAND: find / -name '*.log' -size +100M 2>/dev/null\n"
        "CONFIDENCE: medium\n"
        "WARNING: none\n\n"

        "User: clean up old stuff to free space\n"
        "Assistant:\n"
        "COMMAND: sudo apt-get autoremove\n"
        "CONFIDENCE: low\n"
        "WARNING: Removes packages that may still be needed; verify before running.\n\n"

        "--- RULES ---\n"
        "1. Output EXACTLY three lines (COMMAND, CONFIDENCE, WARNING).\n"
        "2. Use the REAL paths and usernames from the SYSTEM STATE above.\n"
        "3. Never use generic placeholders like '/username'.\n"
        "4. Never use sudo unless explicitly requested.\n"
        "5. Prefer safe flags (e.g. -i for rm).\n"
        "6. CONFIDENCE must reflect how well the command matches the request:\n"
        "   - high: request is unambiguous and command is a standard, direct solution.\n"
        "   - medium: request is somewhat vague or the command makes reasonable assumptions.\n"
        "   - low: request is ambiguous, destructive, or the command is a best guess.\n\n"

        "--- TASK ---\n"
        "Now provide the command for the following request:"
    )

    _session.add_msg_history("user", user_input)

    messages = [{"role": "system", "content": system_prompt}] + _session.history

    _session.prune_msg_history()

    try:
        response = _llm.create_chat_completion(
            messages=messages,
            temperature=0.15,
            max_tokens=150,
        )
        reply = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        return TranslationResult("", "low", "", False, f"Unexpected model response format: {e}")
    except Exception as e:
        return TranslationResult("", "low", "", False, f"Model inference failed: {e}")

    result = _parse_response(reply)
    _session.add_msg_history("assistant", reply)

    return result
