import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, FileText, Copy, Check, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfText, setPdfText] = useState('');
  const [showPdfText, setShowPdfText] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [recognition, setRecognition] = useState(null);
  const [speechSynthesis, setSpeechSynthesis] = useState(null);
  const messagesEndRef = useRef(null);
  const speechRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch PDF text when component mounts
  useEffect(() => {
    fetchPdfText();
    initializeVoiceFeatures();
  }, []);

  const initializeVoiceFeatures = () => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
      };
      
      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(recognitionInstance);
    }

    // Initialize Speech Synthesis
    if ('speechSynthesis' in window) {
      setSpeechSynthesis(window.speechSynthesis);
    }
  };

  const fetchPdfText = async () => {
    try {
      const response = await axios.get('/pdf-text');
      if (response.data.status === 'success') {
        setPdfText(response.data.text);
      }
    } catch (err) {
      console.log('Could not fetch PDF text:', err);
    }
  };

  const copyToClipboard = async (text, messageId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const startListening = () => {
    if (recognition && !isListening) {
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const speakText = (text) => {
    if (speechSynthesis && voiceEnabled) {
      // Stop any current speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      // Try to use a natural voice
      const voices = speechSynthesis.getVoices();
      const naturalVoice = voices.find(voice => 
        voice.name.includes('Google') || 
        voice.name.includes('Microsoft') ||
        voice.name.includes('Natural')
      );
      if (naturalVoice) {
        utterance.voice = naturalVoice;
      }
      
      utterance.onstart = () => {
        setIsSpeaking(true);
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
      };
      
      utterance.onerror = () => {
        setIsSpeaking(false);
      };
      
      speechRef.current = utterance;
      speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (speechSynthesis) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const toggleVoice = () => {
    if (voiceEnabled) {
      stopSpeaking();
    }
    setVoiceEnabled(!voiceEnabled);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post('/chat', {
        message: inputMessage,
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        sources: response.data.sources,
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Speak the AI response if voice is enabled
      if (voiceEnabled) {
        speakText(response.data.response);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error getting response');
      
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error while processing your question. Please try again.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSendMessage(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Bot className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Chat with PDF</h2>
              <p className="text-sm text-gray-600">
                Ask questions about your uploaded PDF document
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowPdfText(!showPdfText)}
              className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center space-x-2 ${
                showPdfText 
                  ? 'bg-primary-600 text-white' 
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>{showPdfText ? 'Hide' : 'Show'} PDF Text</span>
            </button>
            
            {/* Voice Controls */}
            <div className="flex items-center space-x-1 border border-gray-200 rounded-lg p-1">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={!recognition}
                className={`p-2 rounded transition-colors ${
                  isListening 
                    ? 'bg-red-500 text-white' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                } ${!recognition ? 'opacity-50 cursor-not-allowed' : ''}`}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>
              
              <button
                onClick={toggleVoice}
                className={`p-2 rounded transition-colors ${
                  voiceEnabled 
                    ? 'text-green-600 hover:text-green-800 hover:bg-green-100' 
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                }`}
                title={voiceEnabled ? 'Disable voice output' : 'Enable voice output'}
              >
                {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </button>
              
              {isSpeaking && (
                <button
                  onClick={stopSpeaking}
                  className="p-2 text-red-600 hover:text-red-800 hover:bg-red-100 rounded transition-colors"
                  title="Stop speaking"
                >
                  <VolumeX className="h-4 w-4" />
                </button>
              )}
            </div>
            
            <button
              onClick={clearChat}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Clear Chat
            </button>
          </div>
        </div>

        {/* PDF Text Display */}
        {showPdfText && (
          <div className="border-b border-gray-200 p-6 bg-gray-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900">PDF Content</h3>
              <button
                onClick={() => copyToClipboard(pdfText, 'pdf-text')}
                className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
              >
                {copiedMessageId === 'pdf-text' ? (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <div className="max-h-64 overflow-y-auto bg-white border border-gray-200 rounded-lg p-4">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {pdfText || 'No PDF text available'}
              </pre>
            </div>
          </div>
        )}

        {/* Chat Messages */}
        <div className="h-96 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Ask me anything about your PDF document. I can help explain concepts, 
                answer questions, and provide insights based on the content.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-primary-600 text-white'
                      : message.isError
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.sender === 'bot' && (
                      <Bot className="h-4 w-4 text-gray-500 mt-1 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-gray-200">
                          <p className="text-xs text-gray-500 mb-2">📚 Sources:</p>
                          <div className="flex flex-wrap gap-1">
                            {message.sources.map((source, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded-full"
                              >
                                {source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {message.sender === 'bot' && (
                      <div className="flex items-center space-x-1 ml-2">
                        <button
                          onClick={() => copyToClipboard(message.text, message.id)}
                          className="p-1 hover:bg-gray-200 rounded transition-colors"
                          title="Copy message"
                        >
                          {copiedMessageId === message.id ? (
                            <Check className="h-3 w-3 text-green-600" />
                          ) : (
                            <Copy className="h-3 w-3 text-gray-500" />
                          )}
                        </button>
                        {voiceEnabled && (
                          <button
                            onClick={() => speakText(message.text)}
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                            title="Speak message"
                          >
                            <Volume2 className="h-3 w-3 text-blue-500" />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-xs opacity-70">
                      {message.timestamp}
                    </p>
                    {message.sender === 'bot' && (
                      <span className="text-xs opacity-70">✨ AI Assistant</span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary-600" />
                  <span className="text-sm">🤔 Let me think about that...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-6 pb-4">
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Chat Input */}
        <div className="p-6 border-t border-gray-200">
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isListening ? "🎤 Listening... Speak now!" : "Ask a question about your PDF or click the mic to speak..."}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows="2"
                disabled={isLoading}
              />
              
              {/* Voice Input Button */}
              <button
                type="button"
                onClick={isListening ? stopListening : startListening}
                disabled={!recognition || isLoading}
                className={`absolute right-3 top-3 p-2 rounded-full transition-colors ${
                  isListening 
                    ? 'bg-red-500 text-white animate-pulse' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                } ${!recognition || isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>
            </div>
            
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>Send</span>
            </button>
          </form>
          
          {/* Voice Status Indicators */}
          <div className="mt-3 flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              {isListening && (
                <div className="flex items-center space-x-2 text-red-600">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  <span>🎤 Listening...</span>
                </div>
              )}
              {isSpeaking && (
                <div className="flex items-center space-x-2 text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>🔊 Speaking...</span>
                </div>
              )}
            </div>
            
            <div className="text-gray-500">
              {recognition ? '🎤 Voice input available' : '❌ Voice input not supported'}
            </div>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-medium text-blue-900 mb-4 flex items-center">
          <span className="mr-2">💡</span>
          Try asking me these friendly questions:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="text-blue-800 text-sm space-y-2">
            <p className="font-medium">• "Hey, what's this document about?"</p>
            <p className="font-medium">• "Can you break down the main ideas for me?"</p>
            <p className="font-medium">• "What should I focus on here?"</p>
            <p className="font-medium">• "I'm confused about this part, can you help?"</p>
          </div>
          <div className="text-blue-800 text-sm space-y-2">
            <p className="font-medium">• "Explain this like I'm a beginner"</p>
            <p className="font-medium">• "What are the key takeaways?"</p>
            <p className="font-medium">• "Can you help me understand this concept?"</p>
            <p className="font-medium">• "What's the most important thing here?"</p>
          </div>
        </div>
        <div className="mt-4 p-3 bg-white rounded-lg border border-blue-100">
          <p className="text-blue-700 text-sm">
            <span className="font-medium">💬 Pro tip:</span> I'm here to chat like a friend! 
            Feel free to ask follow-up questions, ask for clarifications, or just say "I don't understand" - I'll help you out! 😊
          </p>
        </div>
        
        {/* Voice Instructions */}
        <div className="mt-4 p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
          <h4 className="font-medium text-green-900 mb-2 flex items-center">
            <span className="mr-2">🎤</span>
            Voice Features
          </h4>
          <div className="text-green-800 text-sm space-y-1">
            <p>• <strong>Voice Input:</strong> Click the microphone icon to speak your questions</p>
            <p>• <strong>Voice Output:</strong> AI responses are automatically spoken (toggle with volume icon)</p>
            <p>• <strong>Individual Messages:</strong> Click the speaker icon on any AI message to replay it</p>
            <p>• <strong>Stop Speaking:</strong> Click the stop button to interrupt AI speech</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
