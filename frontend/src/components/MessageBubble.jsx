import React from 'react';
import SourcesList from './SourcesList';

const MessageBubble = ({ message, isUser }) => {
  if (isUser) {
    return (
      <div className="flex justify-end mb-5">
        <div className="max-w-[80%] bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-2xl px-5 py-3.5 shadow-lg hover:shadow-xl transition-shadow">
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed font-medium">{message.query}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-5">
      <div className="max-w-[80%] bg-white/90 backdrop-blur-sm border border-gray-200/50 rounded-2xl px-5 py-4 shadow-soft hover:shadow-lg transition-all">
        <p className="text-gray-800 whitespace-pre-wrap break-words mb-3 leading-relaxed text-sm">{message.answer}</p>
        {message.sources && message.sources.length > 0 && (
          <SourcesList sources={message.sources} />
        )}
        {message.timing && (
          <div className="mt-3 text-xs text-gray-500 flex items-center font-medium">
            <svg className="w-3.5 h-3.5 mr-1.5 text-indigo-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            {message.timing.total.toFixed(2)}s
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;

