import React from 'react';

const LoadingIndicator = () => {
  return (
    <div className="flex items-center justify-start mb-5">
      <div className="max-w-[80%] bg-white/90 backdrop-blur-sm border border-gray-200/50 rounded-2xl px-5 py-4 shadow-soft">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1.5">
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-gray-600 font-medium">Thinking...</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;

