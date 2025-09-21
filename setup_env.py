#!/usr/bin/env python3
"""
Setup script for PDF RAG Chat System
This script helps you configure the environment variables needed for the system.
"""

import os
import sys

def create_env_file():
    """Create .env file with proper configuration"""
    env_content = """# Gemini API Key (for enhanced responses)
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Origins
FRONTEND_URL=http://localhost:3000
"""
    
    env_path = os.path.join("backend", ".env")
    
    if os.path.exists(env_path):
        print(f"✅ .env file already exists at {env_path}")
        return True
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_path}")
        print("📝 Please edit the .env file and add your OpenAI API key if you have one")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'langchain', 'chromadb', 
        'sentence-transformers', 'python-dotenv', 'pypdf2',
        'langchain_google_genai', 'google-generativeai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 PDF RAG Chat System Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    print("\n1. Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n2. Setting up environment...")
    env_ok = create_env_file()
    
    print("\n3. Setup Summary:")
    print("=" * 20)
    
    if deps_ok and env_ok:
        print("✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit backend/.env and add your Gemini API key")
        print("   - Get your key from: https://makersuite.google.com/app/apikey")
        print("2. Install new dependencies: pip install -r requirements.txt")
        print("3. Start the backend: cd backend && python main.py")
        print("4. Start the frontend: cd frontend && npm start")
        print("5. Open http://localhost:3000 in your browser")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
