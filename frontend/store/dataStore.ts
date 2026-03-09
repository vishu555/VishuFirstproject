import { create } from 'zustand';
import api from '../utils/api';

interface Income {
  id: string;
  source: string;
  amount: number;
  date: string;
  notes: string;
}

interface Expense {
  id: string;
  amount: number;
  category: string;
  date: string;
  notes: string;
}

interface Budget {
  id: string;
  category: string;
  limit: number;
  period: string;
  spent: number;
}

interface Analytics {
  total_income: number;
  total_expenses: number;
  remaining_balance: number;
  monthly_income: number;
  monthly_expenses: number;
  savings_rate: number;
}

interface DataState {
  income: Income[];
  expenses: Expense[];
  budgets: Budget[];
  analytics: Analytics | null;
  isLoading: boolean;
  fetchIncome: () => Promise<void>;
  fetchExpenses: () => Promise<void>;
  fetchBudgets: () => Promise<void>;
  fetchAnalytics: () => Promise<void>;
  addIncome: (data: Omit<Income, 'id' | 'created_at'>) => Promise<void>;
  addExpense: (data: Omit<Expense, 'id' | 'created_at'>) => Promise<void>;
  addBudget: (data: Omit<Budget, 'id' | 'spent'>) => Promise<void>;
  deleteIncome: (id: string) => Promise<void>;
  deleteExpense: (id: string) => Promise<void>;
  deleteBudget: (id: string) => Promise<void>;
  refreshAll: () => Promise<void>;
}

export const useDataStore = create<DataState>((set, get) => ({
  income: [],
  expenses: [],
  budgets: [],
  analytics: null,
  isLoading: false,

  fetchIncome: async () => {
    try {
      const response = await api.get('/income');
      set({ income: response.data });
    } catch (error) {
      console.error('Failed to fetch income:', error);
    }
  },

  fetchExpenses: async () => {
    try {
      const response = await api.get('/expenses');
      set({ expenses: response.data });
    } catch (error) {
      console.error('Failed to fetch expenses:', error);
    }
  },

  fetchBudgets: async () => {
    try {
      const response = await api.get('/budget');
      set({ budgets: response.data });
    } catch (error) {
      console.error('Failed to fetch budgets:', error);
    }
  },

  fetchAnalytics: async () => {
    try {
      const response = await api.get('/analytics/summary');
      set({ analytics: response.data });
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  },

  addIncome: async (data) => {
    try {
      await api.post('/income', data);
      await get().fetchIncome();
      await get().fetchAnalytics();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add income');
    }
  },

  addExpense: async (data) => {
    try {
      await api.post('/expenses', data);
      await get().fetchExpenses();
      await get().fetchBudgets();
      await get().fetchAnalytics();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add expense');
    }
  },

  addBudget: async (data) => {
    try {
      await api.post('/budget', data);
      await get().fetchBudgets();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add budget');
    }
  },

  deleteIncome: async (id) => {
    try {
      await api.delete(`/income/${id}`);
      await get().fetchIncome();
      await get().fetchAnalytics();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete income');
    }
  },

  deleteExpense: async (id) => {
    try {
      await api.delete(`/expenses/${id}`);
      await get().fetchExpenses();
      await get().fetchBudgets();
      await get().fetchAnalytics();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete expense');
    }
  },

  deleteBudget: async (id) => {
    try {
      await api.delete(`/budget/${id}`);
      await get().fetchBudgets();
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete budget');
    }
  },

  refreshAll: async () => {
    set({ isLoading: true });
    await Promise.all([
      get().fetchIncome(),
      get().fetchExpenses(),
      get().fetchBudgets(),
      get().fetchAnalytics(),
    ]);
    set({ isLoading: false });
  },
}));