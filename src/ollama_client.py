from llama_cpp import Llama
#from response_parser import response_parser

model_path = "../model.gguf"
llm = Llama.from_pretrained(
    repo_id= "bartowski/Qwen2.5-7B-Instruct-GGUF",
    filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    chat_format="chatml",
    verbose = True)

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

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in Linux and Unix Commands. "
                    "Given a command in english, respond with the proper command in Unix. "
                    "Be precise, factual, and concise. No fluff, no speculation, no references. "
                    "Output ONLY the raw command itself without any markdown formatting, backticks, or quotes. "
                    "Just the plain command text."
                )
            },
            {
                "role": "user",
                "content": llm_input
            }
        ],
        temperature=0.7
    )

    # Extract the actual text from the nested response structure
    return(response["choices"][0]["message"]["content"])

print(ollama_client("give me a command to search for all files that start with the name log and have the file extension .log"))