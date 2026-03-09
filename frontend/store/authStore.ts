import { create } from 'zustand';
import { storage } from '../utils/storage';
import api from '../utils/api';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadStoredAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    try {
      console.log('Login attempt:', { email });
      const response = await api.post('/auth/login', { email, password });
      console.log('Login response received:', response.status);
      const { access_token, user } = response.data;
      
      console.log('Storing auth token...');
      await storage.setItem('authToken', access_token);
      await storage.setItem('userData', JSON.stringify(user));
      
      console.log('Login successful, updating state');
      set({ user, token: access_token, isAuthenticated: true });
    } catch (error: any) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      throw new Error(error.response?.data?.detail || error.message || 'Login failed');
    }
  },

  register: async (name: string, email: string, password: string) => {
    try {
      console.log('Registration attempt:', { name, email });
      const response = await api.post('/auth/register', { name, email, password });
      console.log('Registration response received:', response.status);
      const { access_token, user } = response.data;
      
      console.log('Storing auth token...');
      await storage.setItem('authToken', access_token);
      await storage.setItem('userData', JSON.stringify(user));
      
      console.log('Registration successful, updating state');
      set({ user, token: access_token, isAuthenticated: true });
    } catch (error: any) {
      console.error('Registration error:', error);
      console.error('Error response:', error.response?.data);
      throw new Error(error.response?.data?.detail || error.message || 'Registration failed');
    }
  },

  logout: async () => {
    await storage.deleteItem('authToken');
    await storage.deleteItem('userData');
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadStoredAuth: async () => {
    try {
      const token = await storage.getItem('authToken');
      const userDataStr = await storage.getItem('userData');
      
      if (token && userDataStr) {
        const user = JSON.parse(userDataStr);
        set({ user, token, isAuthenticated: true, isLoading: false });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      set({ isLoading: false });
    }
  },
}));