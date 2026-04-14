from llama_cpp import Llama
import os
import json

# Model path currently unused, pulling directly from hugging face
model_path = "../model.gguf"
llm = Llama.from_pretrained(
    repo_id= "bartowski/Qwen2.5-7B-Instruct-GGUF",
    filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    chat_format="chatml",
    verbose = True)

# Define LLM identity statement
# TODO: Define a more specific and context aware prompt
llm_identity = (
    "You are an expert in Linux and Unix Commands. "
    "Given a command in english, respond with the proper command in Unix. "
    "Be precise, factual, and concise. No fluff, no speculation, no references. "
    "Output ONLY the raw command itself without any markdown formatting, backticks, or quotes. "
    "Just the plain command text."
)

# TODO: Implement OS awareness
# TODO: Implement current directory awareness

# Stores chat history for model context
class ChatSession:

    # Initialize history file for instantiated object
    def __init__(self, chat_history_file="src/chat_history.json"):
        self.chat_history_file = chat_history_file
        self.history = self.load_msg_history()

    # Return history[] array based on content of chat_history.json file
    def load_msg_history(self):
        if os.path.exists(self.chat_history_file):
            try:
                with open(self.chat_history_file, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    # Save message history to file for next use
    def save_msg_history(self):
        try:
            with open(self.chat_history_file, "w") as file:
                json.dump(self.history, file, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")

    # Add message to the history[] array and save it
    def add_msg_history(self, role, msg_content):
        self.history.append({"role": role, "content": msg_content})
        self.save_msg_history()

    # Print the history stored in the history[] array
    def print_msg_history(self):
        print(json.dumps(self.history, indent=2))


# Input coming from cli.py (thorugh main as pipeline)
def ollama_client(llm_input):

    session = ChatSession(chat_history_file="src/chat_history.json")

    # Add current user input to history before sending input to LLM
    session.add_msg_history("user", llm_input)

    # Add llm_identity to session history for context
    messages = [{"role": "system", "content": llm_identity}] + session.history

    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.7
    )

    # Extract the actual text from the nested response structure
    llm_reply = response["choices"][0]["message"]["content"]

    # Add llm reply to chat history for persistence in .json file
    session.add_msg_history("assistant", llm_reply)

    return llm_reply