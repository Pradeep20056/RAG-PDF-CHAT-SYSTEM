#!/usr/bin/env python3
"""
Install dependencies for PDF RAG Chat System
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    packages = [
        "langchain-google-genai",
        "google-generativeai",
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "langchain",
        "langchain-community",
        "pypdf2",
        "chromadb",
        "sentence-transformers",
        "python-dotenv",
        "pydantic",
        "numpy",
        "pandas"
    ]
    
    print("🚀 Installing dependencies for PDF RAG Chat System...")
    print("=" * 50)
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("\n✅ All dependencies installed successfully!")
    return True

def main():
    """Main installation function"""
    if install_packages():
        print("\n📋 Next steps:")
        print("1. Start the backend: cd backend && python main.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
