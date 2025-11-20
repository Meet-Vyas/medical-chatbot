import React, { useState } from 'react';

const SourcesList = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-gray-200/50 pt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-sm text-gray-700 hover:text-indigo-600 transition-colors group"
      >
        <span className="font-semibold flex items-center">
          <svg className="w-4 h-4 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Sources ({sources.length})
        </span>
        <svg
          className={`w-4 h-4 transition-transform duration-200 text-indigo-500 ${isExpanded ? 'transform rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isExpanded && (
        <ul className="mt-3 space-y-2 animate-fadeIn">
          {sources.map((source, index) => (
            <li key={index} className="text-sm text-gray-700 pl-3 border-l-4 border-indigo-400 bg-indigo-50/50 py-2 rounded-r-lg hover:bg-indigo-50 transition-colors">
              <span className="font-semibold text-indigo-700">{source.substance_name}</span>
              <span className="text-gray-500 mx-2">•</span>
              <span className="text-gray-600">{source.section_name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SourcesList;

