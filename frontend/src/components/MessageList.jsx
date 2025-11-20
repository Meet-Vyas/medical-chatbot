import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';

const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8 space-y-2">
      {messages.length === 0 && !isLoading && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center max-w-md">
            <div className="mb-6 flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full blur-xl opacity-50"></div>
                <svg className="w-20 h-20 mx-auto relative text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-display font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Welcome to Medical Knowledge Graph Chatbot
            </h2>
            <p className="text-gray-600 mt-3 font-medium">Ask me about side effects, safety, drug interactions, and more!</p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-full text-xs font-medium">Side Effects</span>
              <span className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">Drug Interactions</span>
              <span className="px-3 py-1.5 bg-pink-100 text-pink-700 rounded-full text-xs font-medium">Safety Information</span>
            </div>
          </div>
        </div>
      )}
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} isUser={message.isUser} />
      ))}
      {isLoading && <LoadingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;

