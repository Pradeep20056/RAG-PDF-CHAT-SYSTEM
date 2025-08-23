import React, { useState } from 'react';
import PDFUpload from './components/PDFUpload';
import PDFViewer from './components/PDFViewer';
import ChatInterface from './components/ChatInterface';
import Whiteboard from './components/Whiteboard';
import { Upload, MessageCircle, Edit3, FileText } from 'lucide-react';

function App() {
  const [currentTab, setCurrentTab] = useState('upload');
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfInfo, setPdfInfo] = useState(null);

  const handlePDFUpload = (file, info) => {
    setPdfFile(file);
    setPdfInfo(info);
    setCurrentTab('viewer');
  };

  const tabs = [
    { id: 'upload', label: 'Upload PDF', icon: Upload },
    { id: 'viewer', label: 'PDF Viewer', icon: FileText, disabled: !pdfFile },
    { id: 'chat', label: 'Chat', icon: MessageCircle, disabled: !pdfFile },
    { id: 'whiteboard', label: 'Whiteboard', icon: Edit3, disabled: !pdfFile },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                PDF RAG Chat System
              </h1>
            </div>
            {pdfInfo && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">Pages:</span> {pdfInfo.pages} | 
                <span className="font-medium ml-2">Chunks:</span> {pdfInfo.chunks}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setCurrentTab(tab.id)}
                  disabled={tab.disabled}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    currentTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : tab.disabled
                      ? 'border-transparent text-gray-400 cursor-not-allowed'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === 'upload' && (
          <PDFUpload onPDFUpload={handlePDFUpload} />
        )}
        
        {currentTab === 'viewer' && pdfFile && (
          <PDFViewer file={pdfFile} />
        )}
        
        {currentTab === 'chat' && pdfFile && (
          <ChatInterface />
        )}
        
        {currentTab === 'whiteboard' && pdfFile && (
          <Whiteboard />
        )}
      </main>
    </div>
  );
}

export default App;
