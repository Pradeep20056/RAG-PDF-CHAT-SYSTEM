import React, { useState, useRef } from 'react';
import PDFViewer from './components/PDFViewer';
import ChatInterface from './components/ChatInterface';

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfInfo, setPdfInfo] = useState(null);
  const [splitPercentage, setSplitPercentage] = useState(50);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef(null);

  const handlePDFUpload = (file, info) => {
    setPdfFile(file);
    setPdfInfo(info);
  };

  const handleMouseDown = (e) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleMouseMove = (e) => {
    if (!isResizing || !containerRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();
    const newPercentage = ((e.clientX - rect.left) / rect.width) * 100;
    const clampedPercentage = Math.min(Math.max(newPercentage, 20), 80); // Min 20%, Max 80%
    setSplitPercentage(clampedPercentage);
  };

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  // Add global mouse events
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  return (
    <div
      ref={containerRef}
      className="h-screen w-screen bg-gray-100 overflow-hidden relative"
    >
      {/* Resizable Split Layout */}
      <div className="flex h-full">
        {/* Chat Section - Left Side */}
        <div
          className="bg-white border-r border-gray-200 flex flex-col"
          style={{ width: `${splitPercentage}%` }}
        >
          <div className="flex-1 overflow-hidden">
            <ChatInterface />
          </div>
        </div>

        {/* Resize Handle */}
        <div
          className="w-1 bg-gray-200 hover:bg-gray-300 cursor-col-resize relative"
          onMouseDown={handleMouseDown}
        >
          <div className="absolute inset-y-0 left-1/2 w-0.5 bg-gray-400 transform -translate-x-1/2"></div>
        </div>

        {/* PDF Viewer Section - Right Side */}
        <div
          className="bg-white flex flex-col"
          style={{ width: `${100 - splitPercentage}%` }}
        >
          <div className="flex-1 overflow-hidden">
            <PDFViewer file={pdfFile} onPDFUpload={handlePDFUpload} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
