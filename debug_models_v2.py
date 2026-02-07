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

print(f"Checking models with key starting with: {api_key[:5]}...")
try:
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
