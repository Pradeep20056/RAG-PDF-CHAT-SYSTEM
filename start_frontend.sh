#!/bin/bash

echo "Starting PDF RAG Chat Frontend..."
echo

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
else
    cd frontend
fi

# Start the development server
echo "Starting React development server..."
npm start
