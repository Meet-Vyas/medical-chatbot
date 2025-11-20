import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { sendQuery, healthCheck } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    // Check backend health on mount
    const checkHealth = async () => {
      try {
        const health = await healthCheck();
        setIsHealthy(health.status === 'healthy');
      } catch (err) {
        setIsHealthy(false);
        setError('Backend is not available. Please make sure the API server is running.');
      }
    };
    checkHealth();
  }, []);

  const handleSend = async (query) => {
    // Add user message
    const userMessage = {
      isUser: true,
      query,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendQuery(query);
      
      // Add bot response
      const botMessage = {
        isUser: false,
        answer: response.answer,
        sources: response.sources,
        timing: response.timing,
        error: response.error,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        isUser: false,
        answer: `Error: ${err.message}`,
        sources: [],
        timing: null,
        error: err.message,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-md border-b border-gray-200/50 px-6 py-5 shadow-soft">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Medical Knowledge Graph Chatbot
            </h1>
            <p className="text-sm text-gray-600 mt-1.5 font-medium">Ask about side effects, safety, interactions, and more</p>
          </div>
          <div className="flex items-center space-x-2.5 bg-gray-50 px-4 py-2 rounded-full border border-gray-200">
            <div className={`w-2.5 h-2.5 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className={`text-sm font-medium ${isHealthy ? 'text-emerald-700' : 'text-red-700'}`}>
              {isHealthy ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 border-l-4 border-red-500 px-5 py-4 mx-4 mt-4 rounded-lg shadow-soft">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input Box */}
      <InputBox onSend={handleSend} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;

