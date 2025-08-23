import React, { useState, useRef, useEffect } from 'react';
import { fabric } from 'fabric';
import { 
  Pen, 
  Square, 
  Circle, 
  Type, 
  RotateCcw, 
  Trash2, 
  Download, 
  Palette,
  MousePointer
} from 'lucide-react';

const Whiteboard = () => {
  const canvasRef = useRef(null);
  const [canvas, setCanvas] = useState(null);
  const [currentTool, setCurrentTool] = useState('select');
  const [currentColor, setCurrentColor] = useState('#ff0000');
  const [brushSize, setBrushSize] = useState(3);
  const [isDrawing, setIsDrawing] = useState(false);

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (canvasRef.current) {
      const fabricCanvas = new fabric.Canvas(canvasRef.current, {
        width: 800,
        height: 600,
        backgroundColor: '#ffffff',
        selection: true,
      });

      // Set default properties
      fabricCanvas.freeDrawingBrush.width = brushSize;
      fabricCanvas.freeDrawingBrush.color = currentColor;

      setCanvas(fabricCanvas);

      return () => {
        fabricCanvas.dispose();
      };
    }
  }, []);

  // Update brush properties when color or size changes
  useEffect(() => {
    if (canvas) {
      canvas.freeDrawingBrush.width = brushSize;
      canvas.freeDrawingBrush.color = currentColor;
    }
  }, [canvas, brushSize, currentColor]);

  const handleToolChange = (tool) => {
    setCurrentTool(tool);
    
    if (canvas) {
      canvas.isDrawingMode = false;
      canvas.selection = true;
      
      switch (tool) {
        case 'pen':
          canvas.isDrawingMode = true;
          canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
          break;
        case 'rectangle':
          canvas.defaultCursor = 'crosshair';
          break;
        case 'circle':
          canvas.defaultCursor = 'crosshair';
          break;
        case 'text':
          canvas.defaultCursor = 'text';
          break;
        case 'select':
          canvas.defaultCursor = 'default';
          break;
        default:
          canvas.defaultCursor = 'default';
      }
    }
  };

  const addRectangle = () => {
    if (canvas) {
      const rect = new fabric.Rect({
        left: 100,
        top: 100,
        width: 100,
        height: 100,
        fill: 'transparent',
        stroke: currentColor,
        strokeWidth: brushSize,
        selectable: true,
      });
      canvas.add(rect);
      canvas.setActiveObject(rect);
    }
  };

  const addCircle = () => {
    if (canvas) {
      const circle = new fabric.Circle({
        left: 100,
        top: 100,
        radius: 50,
        fill: 'transparent',
        stroke: currentColor,
        strokeWidth: brushSize,
        selectable: true,
      });
      canvas.add(circle);
      canvas.setActiveObject(circle);
    }
  };

  const addText = () => {
    if (canvas) {
      const text = new fabric.IText('Type here', {
        left: 100,
        top: 100,
        fontSize: 20,
        fill: currentColor,
        selectable: true,
      });
      canvas.add(text);
      canvas.setActiveObject(text);
    }
  };

  const clearCanvas = () => {
    if (canvas) {
      canvas.clear();
      canvas.backgroundColor = '#ffffff';
      canvas.renderAll();
    }
  };

  const downloadCanvas = () => {
    if (canvas) {
      const dataURL = canvas.toDataURL({
        format: 'png',
        quality: 1
      });
      
      const link = document.createElement('a');
      link.download = 'whiteboard-annotations.png';
      link.href = dataURL;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleMouseDown = (e) => {
    if (currentTool === 'rectangle') {
      setIsDrawing(true);
      const pointer = canvas.getPointer(e.e);
      const rect = new fabric.Rect({
        left: pointer.x,
        top: pointer.y,
        width: 0,
        height: 0,
        fill: 'transparent',
        stroke: currentColor,
        strokeWidth: brushSize,
        selectable: true,
      });
      canvas.add(rect);
      canvas.setActiveObject(rect);
      canvas._currentRect = rect;
    } else if (currentTool === 'circle') {
      setIsDrawing(true);
      const pointer = canvas.getPointer(e.e);
      const circle = new fabric.Circle({
        left: pointer.x,
        top: pointer.y,
        radius: 0,
        fill: 'transparent',
        stroke: currentColor,
        strokeWidth: brushSize,
        selectable: true,
      });
      canvas.add(circle);
      canvas.setActiveObject(circle);
      canvas._currentCircle = circle;
    }
  };

  const handleMouseMove = (e) => {
    if (isDrawing && canvas) {
      const pointer = canvas.getPointer(e.e);
      
      if (currentTool === 'rectangle' && canvas._currentRect) {
        const rect = canvas._currentRect;
        const width = Math.abs(pointer.x - rect.left);
        const height = Math.abs(pointer.y - rect.top);
        rect.set({ width, height });
        canvas.renderAll();
      } else if (currentTool === 'circle' && canvas._currentCircle) {
        const circle = canvas._currentCircle;
        const radius = Math.sqrt(
          Math.pow(pointer.x - circle.left, 2) + 
          Math.pow(pointer.y - circle.top, 2)
        );
        circle.set({ radius });
        canvas.renderAll();
      }
    }
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
    if (canvas) {
      canvas._currentRect = null;
      canvas._currentCircle = null;
    }
  };

  // Add event listeners for drawing shapes
  useEffect(() => {
    if (canvas) {
      canvas.on('mouse:down', handleMouseDown);
      canvas.on('mouse:move', handleMouseMove);
      canvas.on('mouse:up', handleMouseUp);
      
      return () => {
        canvas.off('mouse:down', handleMouseDown);
        canvas.off('mouse:move', handleMouseMove);
        canvas.off('mouse:up', handleMouseUp);
      };
    }
  }, [canvas, currentTool, isDrawing, currentColor, brushSize]);

  const tools = [
    { id: 'select', icon: MousePointer, label: 'Select' },
    { id: 'pen', icon: Pen, label: 'Pen' },
    { id: 'rectangle', icon: Square, label: 'Rectangle' },
    { id: 'circle', icon: Circle, label: 'Circle' },
    { id: 'text', icon: Type, label: 'Text' },
  ];

  const colors = [
    '#ff0000', '#00ff00', '#0000ff', '#ffff00', 
    '#ff00ff', '#00ffff', '#ff8000', '#8000ff'
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Whiteboard</h2>
            <p className="text-gray-600">
              Mark areas of doubt and add annotations to your PDF
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={clearCanvas}
              className="px-4 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Trash2 className="h-4 w-4" />
              <span>Clear</span>
            </button>
            
            <button
              onClick={downloadCanvas}
              className="px-4 py-2 text-sm text-primary-600 hover:text-primary-800 hover:bg-primary-50 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </button>
          </div>
        </div>

        {/* Tools and Controls */}
        <div className="flex flex-wrap items-center justify-between mb-6 gap-4">
          {/* Drawing Tools */}
          <div className="flex items-center space-x-2">
            {tools.map((tool) => {
              const Icon = tool.icon;
              return (
                <button
                  key={tool.id}
                  onClick={() => handleToolChange(tool.id)}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    currentTool === tool.id
                      ? 'border-primary-500 bg-primary-50 text-primary-600'
                      : 'border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-800'
                  }`}
                  title={tool.label}
                >
                  <Icon className="h-5 w-5" />
                </button>
              );
            })}
          </div>

          {/* Color Palette */}
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600">Color:</span>
            <div className="flex space-x-1">
              {colors.map((color) => (
                <button
                  key={color}
                  onClick={() => setCurrentColor(color)}
                  className={`w-6 h-6 rounded-full border-2 transition-transform ${
                    currentColor === color ? 'border-gray-800 scale-110' : 'border-gray-300'
                  }`}
                  style={{ backgroundColor: color }}
                  title={color}
                />
              ))}
            </div>
          </div>

          {/* Brush Size */}
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600">Size:</span>
            <input
              type="range"
              min="1"
              max="20"
              value={brushSize}
              onChange={(e) => setBrushSize(parseInt(e.target.value))}
              className="w-20"
            />
            <span className="text-sm text-gray-600 w-8">{brushSize}</span>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex justify-center">
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
            <canvas ref={canvasRef} className="whiteboard-canvas" />
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">How to use the whiteboard:</h3>
          <ul className="text-blue-800 text-sm space-y-1">
            <li>• <strong>Select:</strong> Click and drag to select objects</li>
            <li>• <strong>Pen:</strong> Draw freehand lines and shapes</li>
            <li>• <strong>Rectangle/Circle:</strong> Click and drag to create shapes</li>
            <li>• <strong>Text:</strong> Click to add text annotations</li>
            <li>• <strong>Color & Size:</strong> Choose colors and adjust brush thickness</li>
            <li>• <strong>Download:</strong> Save your annotations as an image</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Whiteboard;
