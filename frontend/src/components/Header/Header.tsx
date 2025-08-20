import React from 'react';
import { Brain } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">RAG System Web Application</h1>
          </div>
        </div>
        
      </div>
    </div>
  );
};