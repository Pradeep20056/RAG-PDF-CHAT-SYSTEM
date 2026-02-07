import os
import google.generativeai as genai
from dotenv import load_dotenv

# Use absolute path to backend/.env
env_path = r'c:\Users\ks581\OneDrive\Desktop\Progress\PDFRAG\backend\.env'
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print(f"GEMINI_API_KEY not found in {env_path}")
    exit(1)

genai.configure(api_key=api_key)

print("Supported models for bidiGenerateContent:")
try:
    models = genai.list_models()
    for m in models:
        if 'bidiGenerateContent' in m.supported_generation_methods:
            print(f"MODEL_NAME: {m.name}")
except Exception as e:
    print(f"Error: {e}")
