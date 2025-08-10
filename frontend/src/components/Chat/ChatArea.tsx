import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, FileText, Clock } from 'lucide-react';
import { Message, Document } from '../../types';

interface ChatAreaProps {
  messages: Message[];
  selectedDocuments: Document[];
  projectName: string;
  onSendMessage: (content: string) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  selectedDocuments,
  projectName,
  onSendMessage,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50 h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 p-6">
        <div className="flex items-center space-x-3 mb-1">
          <div className="p-1 bg-blue-100 rounded-lg">
            <Sparkles className="w-4 h-4 text-blue-600" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900">Chat</h1>
        </div>
        
        {selectedDocuments.length > 0 && (
          <div className="mt-1">
            <h3 className="text-sm font-medium text-gray-700 mb-1">Selected documents:</h3>
            <div className="flex flex-wrap gap-1">
              {selectedDocuments.map((doc) => (
                <span
                  key={doc.id}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                >
                  <FileText className="w-3 h-3 mr-1" />
                  {doc.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-scroll p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.flatMap((message) => {
            // Split message content into lines and check for image lines
            const lines = message.content.split('\n');
            const result: JSX.Element[] = [];
            lines.forEach((line, index) => {
              const imageMatch = line.match(/^\[IMAGE:(.+)\]$/);
              if (imageMatch && imageMatch[1].trim()) {
                let imgPath = imageMatch[1].trim();
                result.push(
                  <div
                    key={message.id + '-img-' + index}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-3xl ${message.sender === 'user' ? 'ml-12' : 'mr-12'}`}>
                      <img
                        src={imgPath}
                        alt="AI Response"
                        className="my-2 rounded shadow"
                        style={{ maxWidth: '100%' }}
                      />
                    </div>
                  </div>
                );
              } else if (index === 0) {
                // Only render the main message once (for the first line)
                result.push(
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-3xl ${message.sender === 'user' ? 'ml-12' : 'mr-12'}`}>
                      {message.sender === 'ai' && (
                        <div className="flex items-center space-x-2 mb-2">
                          <div className="p-1.5 bg-blue-100 rounded-full">
                            <Sparkles className="w-4 h-4 text-blue-600" />
                          </div>
                          <span className="text-sm font-medium text-gray-700">AI Assistant</span>
                        </div>
                      )}
                      <div
                        className={`p-4 rounded-2xl shadow-sm ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white border border-gray-200'
                        }`}
                      >
                        <div className="prose prose-sm max-w-none">
                          {lines
                            .filter(l => !l.match(/^\[IMAGE:(.+)\]$/))
                            .map((line, idx) => (
                              <div key={idx}>
                                {line.startsWith('**') && line.endsWith('**') ? (
                                  <h4 className={`font-semibold mb-2 ${
                                    message.sender === 'user' ? 'text-white' : 'text-gray-900'
                                  }`}>
                                    {line.replace(/\*\*/g, '')}
                                  </h4>
                                ) : line.match(/^\d+\./) ? (
                                  <div className={`font-medium mb-1 ${
                                    message.sender === 'user' ? 'text-white' : 'text-gray-900'
                                  }`}>
                                    {line}
                                  </div>
                                ) : line.trim() ? (
                                  <p className={`mb-2 last:mb-0 ${
                                    message.sender === 'user' ? 'text-white' : 'text-gray-700'
                                  }`}>
                                    {line}
                                  </p>
                                ) : (
                                  <br />
                                )}
                              </div>
                            ))}
                        </div>
                      </div>
                      <div className="flex items-center justify-end mt-2 space-x-2">
                        <Clock className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500">{message.timestamp}</span>
                      </div>
                    </div>
                  </div>
                );
              }
            });
            return result;
          })}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={`Ask questions about ${projectName}...`}
              className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || selectedDocuments.length === 0}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};