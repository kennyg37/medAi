import axios from 'axios';
import { ChatRequest, ChatResponse, Conversation } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to send message');
      }
      throw new Error('Network error');
    }
  },

  async getConversations(): Promise<Conversation[]> {
    try {
      const response = await api.get<Conversation[]>('/conversations');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to fetch conversations');
      }
      throw new Error('Network error');
    }
  },

  async getConversation(id: string): Promise<Conversation> {
    try {
      const response = await api.get<Conversation>(`/conversations/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to fetch conversation');
      }
      throw new Error('Network error');
    }
  },

  async deleteConversation(id: string): Promise<void> {
    try {
      await api.delete(`/conversations/${id}`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to delete conversation');
      }
      throw new Error('Network error');
    }
  },
}; 