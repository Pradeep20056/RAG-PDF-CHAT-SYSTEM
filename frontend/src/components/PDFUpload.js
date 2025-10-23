import React, { useState, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import axios from 'axios';

const PDFUpload = ({ onPDFUpload }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  }, []);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/upload-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      onPDFUpload(file, response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading PDF');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError('');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your PDF Document
        </h2>
        <p className="text-lg text-gray-600">
          Upload a PDF file to start chatting with AI about its content
        </p>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-8 text-center hover:border-primary-400 transition-colors">
        {!file ? (
          <div>
            <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <div className="space-y-4">
              <p className="text-lg text-gray-600">
                Drag and drop your PDF here, or{' '}
                <label className="text-primary-600 hover:text-primary-500 cursor-pointer font-medium">
                  browse files
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF files up to 10MB
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-3">
              <FileText className="h-8 w-8 text-primary-600" />
              <div className="text-left">
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={removeFile}
                className="p-1 hover:bg-gray-100 rounded-full"
              >
                <X className="h-5 w-5 text-gray-400" />
              </button>
            </div>
            
            {!isUploading ? (
              <button
                onClick={handleUpload}
                className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Upload PDF
              </button>
            ) : (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">
                  Uploading... {uploadProgress}%
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-medium text-blue-900 mb-2">How it works:</h3>
        <ul className="text-blue-800 text-sm space-y-1">
          <li>• Upload your PDF document</li>
          <li>• The system will process and analyze the content</li>
          <li>• Ask questions about the PDF in the chat section</li>
          <li>• Use the whiteboard to mark areas of doubt</li>
        </ul>
      </div>
    </div>
  );
};

export default PDFUpload;
