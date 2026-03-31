import ollama
from response_parser import response_parser

MODEL = 'deepseek-r1:8b'  # Change this to your preferred model

# Define LLM identity statement
lm_identity = (
    "You are an expert in Linux and Unix Commands. "
    "Given a command in english, respond with the proper command in Unix. "
    "Be precise, factual, and concise. No fluff, no speculation, no references. "
    "Output ONLY the raw command itself without any markdown formatting, backticks, or quotes. "
    "Just the plain command text."
)

# Input coming from cli.py (thorugh main as pipeline)
def ollama_client(llm_input):

    try:
        print("Initializing Ollama...")
        llm_output = ollama.chat(
            model=MODEL,
            messages=llm_input
        )

        return llm_output

    except Exception as e:
        print(e)