import { create } from 'zustand';
import { storage } from '../utils/storage';
import api from '../utils/api';

interface User {
  id: string;
  name: string;
  email: string;
  currency?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, currency?: string) => Promise<void>;
  updateProfile: (name?: string, currency?: string) => Promise<void>;
  logout: () => Promise<void>;
  loadStoredAuth: () => Promise<void>;
  getCurrency: () => string;
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

  register: async (name: string, email: string, password: string, currency: string = 'USD') => {
    try {
      console.log('Registration attempt:', { name, email, currency });
      const response = await api.post('/auth/register', { name, email, password, currency });
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

  updateProfile: async (name?: string, currency?: string) => {
    try {
      const response = await api.put('/profile', { name, currency });
      const { user } = response.data;
      
      await storage.setItem('userData', JSON.stringify(user));
      set({ user });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Update failed');
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

  getCurrency: () => {
    const state = useAuthStore.getState();
    return state.user?.currency || 'USD';
  },
}));