#!/usr/bin/env python3
"""
Demo script for the PDF RAG Chat System
This script demonstrates the RAG functionality with sample text
"""

import asyncio
import tempfile
import os
from backend.main import app
from fastapi.testclient import TestClient

# Sample text for demonstration
SAMPLE_TEXT = """
Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.

There are three main types of machine learning:

1. Supervised Learning: The algorithm is trained on labeled data, learning to map inputs to outputs.
2. Unsupervised Learning: The algorithm finds hidden patterns in unlabeled data.
3. Reinforcement Learning: The algorithm learns by interacting with an environment and receiving rewards.

Key Concepts:
- Training Data: The dataset used to train the model
- Features: The input variables used for prediction
- Labels: The output variables we want to predict
- Model: The learned function that maps inputs to outputs
- Overfitting: When a model performs well on training data but poorly on new data
- Underfitting: When a model is too simple to capture the underlying patterns

Common Algorithms:
- Linear Regression: For predicting continuous values
- Logistic Regression: For binary classification
- Decision Trees: For both classification and regression
- Random Forests: Ensemble method using multiple decision trees
- Support Vector Machines: For classification with clear margins
- Neural Networks: Deep learning models for complex patterns

Applications:
- Image Recognition: Identifying objects in images
- Natural Language Processing: Understanding and generating text
- Recommendation Systems: Suggesting products or content
- Fraud Detection: Identifying suspicious transactions
- Medical Diagnosis: Assisting doctors with patient diagnosis
- Autonomous Vehicles: Self-driving cars and drones

Challenges:
- Data Quality: Poor data leads to poor models
- Bias: Models can inherit biases from training data
- Interpretability: Complex models are hard to understand
- Scalability: Training large models requires significant resources
- Privacy: Balancing model performance with data privacy

Future Directions:
- Automated Machine Learning (AutoML): Automating the ML pipeline
- Federated Learning: Training models across distributed data
- Explainable AI: Making models more interpretable
- Edge Computing: Running models on devices instead of cloud
- Quantum Machine Learning: Leveraging quantum computing for ML
"""

def create_sample_pdf():
    """Create a sample PDF file for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            c = canvas.Canvas(tmp_file.name, pagesize=letter)
            width, height = letter
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Machine Learning Fundamentals")
            
            # Add content
            c.setFont("Helvetica", 12)
            y_position = height - 100
            lines = SAMPLE_TEXT.split('\n')
            
            for line in lines:
                if line.strip():
                    if line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                        c.setFont("Helvetica-Bold", 12)
                    elif line.startswith('Key Concepts:') or line.startswith('Common Algorithms:') or line.startswith('Applications:') or line.startswith('Challenges:') or line.startswith('Future Directions:'):
                        c.setFont("Helvetica-Bold", 14)
                        y_position -= 20
                    elif line.startswith('- '):
                        c.setFont("Helvetica", 11)
                    else:
                        c.setFont("Helvetica", 12)
                    
                    # Check if we need a new page
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                        c.setFont("Helvetica", 12)
                    
                    c.drawString(50, y_position, line)
                    y_position -= 20
            
            c.save()
            return tmp_file.name
    except ImportError:
        print("reportlab not installed. Creating text file instead.")
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as tmp_file:
            tmp_file.write(SAMPLE_TEXT)
            return tmp_file.name

def test_rag_system():
    """Test the RAG system with sample queries"""
    client = TestClient(app)
    
    print("🚀 Testing PDF RAG Chat System")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = client.get("/pdf-info")
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return
    
    # Test 2: Upload sample document
    print("\n📄 Testing document upload...")
    
    # Create sample file
    sample_file_path = create_sample_pdf()
    file_extension = sample_file_path.split('.')[-1]
    
    with open(sample_file_path, 'rb') as f:
        files = {'file': (f'sample.{file_extension}', f, f'application/{file_extension}')}
        response = client.post("/upload-pdf", files=files)
    
    if response.status_code == 200:
        print("✅ Document uploaded successfully")
        print(f"   Pages: {response.json().get('pages', 'Unknown')}")
        print(f"   Chunks: {response.json().get('chunks', 'Unknown')}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 3: Test chat functionality
    print("\n💬 Testing chat functionality...")
    
    test_questions = [
        "What is machine learning?",
        "What are the three main types of machine learning?",
        "What is overfitting?",
        "Give me examples of machine learning applications",
        "What are the main challenges in machine learning?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Q{i}: {question}")
        
        response = client.post("/chat", json={"message": question})
        
        if response.status_code == 200:
            answer = response.json().get('response', 'No response')
            sources = response.json().get('sources', [])
            
            # Truncate long answers for display
            if len(answer) > 200:
                answer = answer[:200] + "..."
            
            print(f"   A{i}: {answer}")
            if sources:
                print(f"   Sources: {', '.join(sources)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    
    # Clean up
    try:
        os.unlink(sample_file_path)
    except:
        pass
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\nTo run the full system:")
    print("1. Start backend: python backend/main.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")

if __name__ == "__main__":
    test_rag_system()
