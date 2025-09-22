#!/usr/bin/env python3
"""
Test script to check if all dependencies are properly installed
Run this to diagnose package or API key issues
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    packages = [
        ("fastapi", "FastAPI"),
        ("langchain", "LangChain"),
        ("langchain.document_loaders", "LangChain Document Loaders"),
        ("langchain.text_splitter", "LangChain Text Splitter"),
        ("langchain.embeddings", "LangChain Embeddings"),
        ("langchain.vectorstores", "LangChain Vector Stores"),
        ("langchain.chains", "LangChain Chains"),
        ("langchain_google_genai", "LangChain Google Gemini"),
        ("google.generativeai", "Google Generative AI"),
        ("sentence_transformers", "Sentence Transformers"),
        ("chromadb", "ChromaDB"),
        ("pydantic", "Pydantic"),
        ("uvicorn", "Uvicorn"),
    ]
    
    results = {}
    for package, name in packages:
        try:
            if "." in package:
                module_name, submodule = package.split(".", 1)
                module = __import__(module_name)
                getattr(module, submodule)
            else:
                __import__(package)
            results[package] = f"✅ {name}"
            print(f"  ✅ {name}")
        except ImportError as e:
            results[package] = f"❌ {name}: {str(e)}"
            print(f"  ❌ {name}: {str(e)}")
        except Exception as e:
            results[package] = f"⚠️  {name}: {str(e)}"
            print(f"  ⚠️  {name}: {str(e)}")
    
    return results

def test_api_keys():
    """Test if API keys are properly configured"""
    print("\n🔑 Testing API keys...")
    
    load_dotenv()
    
    api_keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    }
    
    results = {}
    for key_name, key_value in api_keys.items():
        if key_value and key_value != "your_gemini_api_key_here":
            results[key_name] = f"✅ Set (length: {len(key_value)})"
            print(f"  ✅ {key_name}: Set (length: {len(key_value)})")
        else:
            results[key_name] = "❌ Not set or invalid"
            print(f"  ❌ {key_name}: Not set or invalid")
    
    return results

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test PDF loader
        from langchain.document_loaders import PyPDFLoader
        print("  ✅ PyPDFLoader import successful")
    except Exception as e:
        print(f"  ❌ PyPDFLoader import failed: {str(e)}")
        return False
    
    try:
        # Test embeddings
        from langchain.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        test_embedding = embeddings.embed_query("test")
        print(f"  ✅ Embeddings working (dimension: {len(test_embedding)})")
    except Exception as e:
        print(f"  ❌ Embeddings test failed: {str(e)}")
        return False
    
    try:
        # Test Gemini if key is available
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_key, temperature=0)
            print("  ✅ Gemini LLM initialization successful")
        else:
            print("  ⚠️  Gemini key not set, skipping Gemini test")
    except Exception as e:
        print(f"  ❌ Gemini test failed: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 PDF RAG System Dependency Test")
    print("=" * 50)
    
    # Test imports
    import_results = test_imports()
    
    # Test API keys
    api_results = test_api_keys()
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 50)
    
    failed_imports = [pkg for pkg, result in import_results.items() if result.startswith("❌")]
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        print("\n💡 To fix import issues, run:")
        print("   pip install fastapi langchain langchain-google-genai sentence-transformers chromadb pydantic uvicorn python-dotenv")
    else:
        print("✅ All imports successful")
    
    failed_apis = [key for key, result in api_results.items() if result.startswith("❌")]
    if failed_apis:
        print(f"❌ Missing API keys: {', '.join(failed_apis)}")
        print("\n💡 To fix API key issues:")
        print("   1. Create a .env file in the backend directory")
        print("   2. Add: GEMINI_API_KEY=your_actual_gemini_api_key")
        print("   3. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    else:
        print("✅ All API keys configured")
    
    if functionality_ok:
        print("✅ Basic functionality tests passed")
    else:
        print("❌ Some functionality tests failed")
    
    print("\n🔧 Next steps:")
    if failed_imports or failed_apis or not functionality_ok:
        print("   1. Fix the issues above")
        print("   2. Run this test again: python test_dependencies.py")
        print("   3. Start the server: python main.py")
    else:
        print("   ✅ Everything looks good! Start the server: python main.py")

if __name__ == "__main__":
    main()
