from llama_cpp import Llama
import os
import json
#from response_parser import response_parser

model_path = "../model.gguf"
llm = Llama.from_pretrained(
    repo_id= "bartowski/Qwen2.5-7B-Instruct-GGUF",
    filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    chat_format="chatml",
    verbose = True)

# Define LLM identity statement
llm_identity = (
    "You are an expert in Linux and Unix Commands. "
    "Given a command in english, respond with the proper command in Unix. "
    "Be precise, factual, and concise. No fluff, no speculation, no references. "
    "Output ONLY the raw command itself without any markdown formatting, backticks, or quotes. "
    "Just the plain command text."
)

# Stores chat history for model context
class ChatSession:

    #TODO: Manage token limits in alignment with selected model

    # Initialize history file for instantiated object
    def __init__(self, chat_history_file = "chat_history.json", history = {}):
        self.chat_history_file = chat_history_file
        self.history = self.load_msg_history()

    # Return history[] array based on content of chat_history.json file
    def load_msg_history(self):

        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "w") as file:
                self.history = json.load(file)
        
        return []

    # Add message to the history[] array pulled from chat_history.json
    def add_msg_history(self, role, msg_content):

        self.history.append({"role" : role, "content" : msg_content})

    # Print the history stored in the history[] array
    def print_msg_history(self):

        print(self.history)



# Input coming from cli.py (thorugh main as pipeline)
def ollama_client(llm_input):

    session = ChatSession(
        chat_history_file="chat_history.json"
    )

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": llm_identity
            },
            {
                "role": "user",
                "content": llm_input
            }
        ],
        temperature=0.7
    )

    # Extract the actual text from the nested response structure
    llm_reply = response["choices"][0]["message"]["content"]

    # Add llm reply to chat history for context
    session.add_msg_history("user", llm_input)
    session.print_msg_history()

    return llm_reply

print(ollama_client("give me a command to search for all files that start with the name log and have the file extension .log"))