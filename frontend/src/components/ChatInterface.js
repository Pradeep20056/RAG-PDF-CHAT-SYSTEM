import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Copy, Check, Mic, MicOff, Radio, MessageSquare } from 'lucide-react';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [speechMode, setSpeechMode] = useState(false);
  const [speechModeLoading, setSpeechModeLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
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

  const toggleSpeechMode = async () => {
    if (speechModeLoading) return;

    setSpeechModeLoading(true);
    try {
      if (speechMode) {
        // Stop speech mode
        const response = await axios.post('/speech-mode/stop');
        if (response.data.status === 'stopped' || response.data.status === 'not_running') {
          setSpeechMode(false);
        }
      } else {
        // Start speech mode
        const response = await axios.post('/speech-mode/start');
        if (response.data.status === 'started') {
          setSpeechMode(true);
        }
      }
    } catch (error) {
      console.error('Error toggling speech mode:', error);
      setError('Failed to toggle speech mode. Please try again.');
    } finally {
      setSpeechModeLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Speech Mode Toggle Button */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex justify-center">
          <button
            onClick={toggleSpeechMode}
            disabled={speechModeLoading}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full font-medium transition-all ${
              speechMode
                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
            } ${speechModeLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            title={speechMode ? 'Switch to Chat Mode' : 'Switch to Speech Mode'}
          >
            {speechModeLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : speechMode ? (
              <MessageSquare className="h-4 w-4" />
            ) : (
              <Radio className="h-4 w-4" />
            )}
            <span>
              {speechModeLoading
                ? (speechMode ? 'Stopping Speech Mode...' : 'Starting Speech Mode...')
                : (speechMode ? 'Chat Mode' : 'Speech Mode')
              }
            </span>
          </button>
        </div>
      </div>

      {/* Chat Messages - Full Height */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
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

        {/* Speech Mode UI */}
        {speechMode && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center">
              <div className="relative mb-8">
                <div className="w-48 h-48 mx-auto bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                  <div className="w-32 h-32 bg-white rounded-full flex items-center justify-center">
                    <Radio className="h-16 w-16 text-blue-600" />
                  </div>
                </div>
                {/* Animated pulse rings */}
                <div className="absolute inset-0 w-48 h-48 mx-auto rounded-full border-4 border-blue-300 animate-ping opacity-20"></div>
                <div className="absolute inset-0 w-48 h-48 mx-auto rounded-full border-4 border-purple-300 animate-ping opacity-10" style={{animationDelay: '0.5s'}}></div>
              </div>

              <h2 className="text-2xl font-bold text-gray-800 mb-4">Speech Mode Active</h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                I'm listening and ready to help! Speak naturally and I'll respond with information from your PDF.
              </p>

              <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Listening</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                  <span>Processing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
                  <span>Ready</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="px-4 pb-3">
            <div className="p-2 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-xs">{error}</p>
            </div>
          </div>
        )}

        {/* Chat Input - Only show when not in speech mode */}
        {!speechMode && (
          <div className="p-4 border-t border-gray-200 bg-white">
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
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1 text-sm"
            >
              <Send className="h-3 w-3" />
              <span>Send</span>
            </button>
          </form>
        </div>
        )}
    </div>
  );
};

export default ChatInterface;
