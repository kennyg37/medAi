import React, { useState, useEffect } from 'react';
import ChatContainer from './components/ChatContainer';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import { Message, Conversation } from './types';
import { chatService } from './services/api';

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const conversations = await chatService.getConversations();
      setConversations(conversations);
    } catch (err) {
      console.error('Error loading conversations:', err);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const newMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, newMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage({
        message: message,
        conversation_id: currentConversation?.id
      });
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (!currentConversation) {
        // Create new conversation
        const newConversation: Conversation = {
          id: response.conversation_id,
          title: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
          messages: [newMessage, assistantMessage],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setCurrentConversation(newConversation);
        setConversations(prev => [newConversation, ...prev]);
      } else {
        // Update existing conversation
        const updatedConversation = {
          ...currentConversation,
          messages: [...currentConversation.messages, newMessage, assistantMessage],
          updated_at: new Date().toISOString()
        };
        setCurrentConversation(updatedConversation);
        setConversations(prev => 
          prev.map(conv => 
            conv.id === currentConversation.id ? updatedConversation : conv
          )
        );
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConversationSelect = async (conversation: Conversation) => {
    setCurrentConversation(conversation);
    setMessages(conversation.messages);
    setSidebarOpen(false); // Close sidebar on mobile
  };

  const handleNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setSidebarOpen(false); // Close sidebar on mobile
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await chatService.deleteConversation(conversationId);
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Error deleting conversation:', err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <Sidebar
          conversations={conversations}
          currentConversation={currentConversation}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Mobile header */}
        <div className="lg:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-900">MedAI Chatbot</h1>
          <div className="w-10"></div> {/* Spacer for centering */}
        </div>

        {/* Chat container */}
        <div className="flex-1 overflow-hidden">
          <ChatContainer 
            messages={messages} 
            loading={loading}
            error={error}
          />
        </div>

        {/* Chat input */}
        <div className="border-t border-gray-200 bg-white p-4">
          <ChatInput 
            onSendMessage={handleSendMessage} 
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

export default App; 