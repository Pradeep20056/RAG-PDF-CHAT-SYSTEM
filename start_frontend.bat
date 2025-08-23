@echo off
echo Starting PDF RAG Chat Frontend...
echo.

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
) else (
    cd frontend
)

REM Start the development server
echo Starting React development server...
npm start

pause
