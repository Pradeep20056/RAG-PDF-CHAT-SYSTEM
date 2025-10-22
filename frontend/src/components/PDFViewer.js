import React, { useState, useRef, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Download, Upload, FileText, X, RotateCcw, PenTool, Palette, Eraser, Save } from 'lucide-react';
import axios from 'axios';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PDFViewer = ({ file, onPDFUpload }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [pageInput, setPageInput] = useState('');

  // Drawing functionality state
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [selectedColor, setSelectedColor] = useState('#3b82f6');
  const [pencilSize, setPencilSize] = useState(3);
  const [isDrawing, setIsDrawing] = useState(false);
  const canvasRef = useRef(null);
  const contextRef = useRef(null);

  // Available colors and sizes
  const colors = [
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Red', value: '#ef4444' },
    { name: 'Green', value: '#10b981' },
    { name: 'Purple', value: '#8b5cf6' },
    { name: 'Black', value: '#1f2937' }
  ];

  const pencilSizes = [1, 3, 5, 8, 12];

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
  };

  const changePage = (offset) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      return Math.min(Math.max(1, newPageNumber), numPages);
    });
  };

  const previousPage = () => changePage(-1);
  const nextPage = () => changePage(1);

  const zoomIn = () => setScale(prevScale => Math.min(prevScale + 0.2, 3.0));
  const zoomOut = () => setScale(prevScale => Math.max(prevScale - 0.2, 0.5));

  const downloadPDF = () => {
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setSelectedFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('https://rag-pdf-chat-system.onrender.com/upload-pdf', formData, {
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

      onPDFUpload(selectedFile, response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading PDF');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setSelectedFile(null);
    }
  };

  const handlePageJump = (e) => {
    e.preventDefault();
    const pageNum = parseInt(pageInput);
    if (pageNum >= 1 && pageNum <= (numPages || 1)) {
      setPageNumber(pageNum);
      setPageInput('');
    } else {
      setError(`Please enter a valid page number (1-${numPages || 1})`);
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleNewPDFUpload = () => {
    // Reset the current PDF
    onPDFUpload(null, null);
  };

  // Drawing functionality
  const startDrawing = ({ nativeEvent }) => {
    if (!isDrawingMode || !canvasRef.current) return;

    const { offsetX, offsetY } = nativeEvent;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    context.beginPath();
    context.moveTo(offsetX, offsetY);
    context.lineWidth = pencilSize;
    context.lineCap = 'round';
    context.strokeStyle = selectedColor;
    contextRef.current = context;
    setIsDrawing(true);
  };

  const draw = ({ nativeEvent }) => {
    if (!isDrawing || !isDrawingMode || !contextRef.current) return;

    const { offsetX, offsetY } = nativeEvent;
    const context = contextRef.current;

    context.lineTo(offsetX, offsetY);
    context.stroke();
  };

  const stopDrawing = () => {
    if (contextRef.current) {
      contextRef.current.closePath();
    }
    setIsDrawing(false);
  };

  const clearDrawing = () => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      context.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  const saveDrawing = () => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const link = document.createElement('a');
      link.download = `drawing_page_${pageNumber}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  };

  const toggleDrawingMode = () => {
    setIsDrawingMode(!isDrawingMode);
    if (!isDrawingMode) {
      // Initialize canvas when entering drawing mode
      setTimeout(() => {
        if (canvasRef.current) {
          const canvas = canvasRef.current;
          const container = canvas.parentElement;
          if (container) {
            const rect = container.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;

            const context = canvas.getContext('2d');
            context.lineCap = 'round';
            context.lineJoin = 'round';
          }
        }
      }, 100);
    }
  };

  // Resize canvas when scale changes or page changes
  useEffect(() => {
    if (isDrawingMode && canvasRef.current) {
      const canvas = canvasRef.current;
      const container = canvas.parentElement;
      if (container) {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;

        // Clear any existing drawing when resizing
        const context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  }, [scale, isDrawingMode, pageNumber]);

  // Initialize canvas when PDF loads
  useEffect(() => {
    if (isDrawingMode && numPages && canvasRef.current) {
      const canvas = canvasRef.current;
      const container = canvas.parentElement;
      if (container) {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;

        const context = canvas.getContext('2d');
        context.lineCap = 'round';
        context.lineJoin = 'round';
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  }, [numPages, isDrawingMode]);

  // Show upload area if no file is uploaded
  if (!file) {
    return (
      <div className="h-full flex flex-col bg-white">
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-sm">
            {/* File Upload Area */}
            <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
              {!selectedFile ? (
                <div>
                  <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">
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
                    <p className="text-xs text-gray-500">
                      Supports PDF files up to 10MB
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-center space-x-2">
                    <FileText className="h-6 w-6 text-primary-600" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 text-sm">{selectedFile.name}</p>
                      <p className="text-xs text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={removeFile}
                      className="p-1 hover:bg-gray-100 rounded-full"
                    >
                      <X className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>

                  {!isUploading ? (
                    <button
                      onClick={handleUpload}
                      className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm w-full"
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
                      <p className="text-xs text-gray-600">
                        Uploading... {uploadProgress}%
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-xs">{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Show PDF viewer if file is uploaded
  return (
    <div className="h-full flex flex-col bg-white">
      {/* PDF Controls */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          {/* Navigation Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={previousPage}
              disabled={pageNumber <= 1}
              className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>

            <span className="text-xs text-gray-600 min-w-[60px] text-center">
              {pageNumber} / {numPages || '...'}
            </span>

            <button
              onClick={nextPage}
              disabled={pageNumber >= (numPages || 1)}
              className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

          {/* Page Jump */}
          <form onSubmit={handlePageJump} className="flex items-center space-x-2">
            <span className="text-xs text-gray-600">Go to:</span>
            <input
              type="number"
              value={pageInput}
              onChange={(e) => setPageInput(e.target.value)}
              placeholder="Page"
              min="1"
              max={numPages || 1}
              className="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
            >
              Go
            </button>
          </form>

          {/* Zoom Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={zoomOut}
              disabled={scale <= 0.5}
              className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ZoomOut className="h-4 w-4" />
            </button>

            <span className="text-xs text-gray-600 min-w-[35px] text-center">
              {Math.round(scale * 100)}%
            </span>

            <button
              onClick={zoomIn}
              disabled={scale >= 3.0}
              className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Drawing Tools */}
          <div className="flex items-center space-x-2 border-l border-gray-300 pl-2 ml-2">
            <button
              onClick={toggleDrawingMode}
              className={`p-1 rounded transition-colors ${
                isDrawingMode
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              title={isDrawingMode ? 'Exit Drawing Mode' : 'Enter Drawing Mode'}
            >
              <PenTool className="h-4 w-4" />
            </button>

            {isDrawingMode && (
              <>
                {/* Color Picker */}
                <div className="flex items-center space-x-1">
                  {colors.map((color) => (
                    <button
                      key={color.value}
                      onClick={() => setSelectedColor(color.value)}
                      className={`w-6 h-6 rounded-full border-2 transition-all ${
                        selectedColor === color.value
                          ? 'border-gray-800 scale-110'
                          : 'border-gray-300 hover:scale-105'
                      }`}
                      style={{ backgroundColor: color.value }}
                      title={color.name}
                    />
                  ))}
                </div>

                {/* Pencil Size Selector */}
                <div className="flex items-center space-x-1">
                  {pencilSizes.map((size) => (
                    <button
                      key={size}
                      onClick={() => setPencilSize(size)}
                      className={`w-8 h-8 rounded border-2 transition-all ${
                        pencilSize === size
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                      title={`Size ${size}`}
                    >
                      <div
                        className="w-full h-full rounded-full bg-current opacity-60"
                        style={{
                          transform: `scale(${size / 8})`,
                          backgroundColor: selectedColor
                        }}
                      />
                    </button>
                  ))}
                </div>

                <button
                  onClick={clearDrawing}
                  className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                  title="Clear Drawing"
                >
                  <Eraser className="h-4 w-4" />
                </button>

                <button
                  onClick={saveDrawing}
                  className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                  title="Save Drawing"
                >
                  <Save className="h-4 w-4" />
                </button>
              </>
            )}
          </div>

          <span className="text-xs text-gray-500 truncate max-w-32">
            {file.name}
          </span>
          <button
            onClick={handleNewPDFUpload}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Upload New PDF"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            onClick={downloadPDF}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Download PDF"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* PDF Display */}
      <div className="flex-1 flex justify-center items-start overflow-auto bg-gray-100 p-4">
        <div className="relative">
          {loading && (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <span className="ml-3 text-gray-600">Loading PDF...</span>
            </div>
          )}

          <Document
            file={file}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(error) => {
              console.error('Error loading PDF:', error);
              setLoading(false);
            }}
            loading={null}
          >
            <div className="relative">
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
              {/* Drawing Canvas Overlay */}
              {isDrawingMode && (
                <canvas
                  ref={canvasRef}
                  className="absolute top-0 left-0 cursor-crosshair"
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={stopDrawing}
                  onMouseLeave={stopDrawing}
                  style={{
                    pointerEvents: isDrawingMode ? 'auto' : 'none',
                    zIndex: 10,
                    width: '100%',
                    height: '100%'
                  }}
                />
              )}
            </div>
          </Document>
        </div>
      </div>

      {/* Page Navigation */}
      {numPages && (
        <div className="flex justify-center p-2 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPageNumber(1)}
              disabled={pageNumber <= 1}
              className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              First
            </button>

            <button
              onClick={() => setPageNumber(numPages)}
              disabled={pageNumber >= numPages}
              className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Last
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PDFViewer;
