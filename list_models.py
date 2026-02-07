import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models...")
for model in client.models.list():
    if "embed" in model.name.lower():
        print(f"Name: {model.name}, Supported Methods: {model.supported_generation_methods}")
