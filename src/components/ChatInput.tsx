import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  loading?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, loading = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="flex items-end space-x-3">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about any medical topic..."
          disabled={loading}
          className="
            w-full resize-none rounded-lg border border-gray-300 px-4 py-3 pr-12
            focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none
            disabled:bg-gray-50 disabled:text-gray-500
            placeholder-gray-400 text-sm leading-relaxed
            min-h-[44px] max-h-[120px]
          "
          rows={1}
        />
        
        {/* Character count */}
        {message.length > 0 && (
          <div className="absolute bottom-2 right-3 text-xs text-gray-400">
            {message.length}
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={!message.trim() || loading}
        className="
          flex-shrink-0 w-12 h-12 rounded-lg bg-blue-500 text-white
          hover:bg-blue-600 focus:bg-blue-600 focus:ring-2 focus:ring-blue-200
          disabled:bg-gray-300 disabled:cursor-not-allowed
          transition-colors duration-200 flex items-center justify-center
        "
      >
        {loading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </button>
    </form>
  );
};

export default ChatInput; 