from multimodel_inference import ModelInference, Message
from dotenv import load_dotenv
import os

# Load the Env with the AI vendor details
load_dotenv()

# Load the variables
wx_api_key = os.getenv("WATSONX_API_KEY")
wx_api_base = os.getenv("WATSONX_URL")
ollama_api_base = os.getenv("OLLAMA_URL")
default_params = {"project_id": os.getenv("WATSONX_PROJECT_ID")}


def main():
    model_inf_ollama = ModelInference(
        model="ollama/llama3.2:3b", # Change provider as needed
        #api_key = api_key,
        api_base = ollama_api_base,
        max_tokens=150,
        temperature=0.5,
        default_params = default_params
    )
    model_inf_wx = ModelInference(
        model="watsonx/meta-llama/llama-3-3-70b-instruct", 
        api_key = wx_api_key,
        api_base = wx_api_base,
        max_tokens=150,
        temperature=0.5,
        default_params = default_params
    )

    print(model_inf_ollama)
    print(model_inf_wx)

    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What's the weather like in Paris today?")
    ]

    # Synchronous generation
    output = model_inf_ollama.generate_text(messages)
    print("Generated from ollama:", output)
    print("================XXXXXX=================")

    output = model_inf_wx.generate_text(messages)
    print("Generated from WatsonX:", output)

    # Streaming generation
    # stream_chunks = model_inf.generate_text_stream(messages)
    # print("Streamed:")
    # print("".join(stream_chunks))

if __name__ == "__main__":
    main()
