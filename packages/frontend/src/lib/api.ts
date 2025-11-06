import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging (development only)
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Transaction API
// ============================================================================

export const transactionsApi = {
  getAll: () => api.get('/transactions'),
  getById: (id: string) => api.get(`/transactions/${id}`),
  create: (data: any) => api.post('/transactions', data),
  update: (id: string, data: any) => api.patch(`/transactions/${id}`, data),
  delete: (id: string) => api.delete(`/transactions/${id}`),
  advanceStage: (id: string, data?: any) => api.post(`/transactions/${id}/advance-stage`, data),
  depositEarnestMoney: (id: string, amount: number) =>
    api.post(`/transactions/${id}/deposit-earnest-money`, { amount }),
  verifyFunds: (id: string, method?: string) =>
    api.post(`/transactions/${id}/verify-funds`, { method }),
  getProgress: (id: string) => api.get(`/transactions/${id}/progress`),
};

// ============================================================================
// Task API
// ============================================================================

export const tasksApi = {
  getAll: (params?: Record<string, any>) => api.get('/tasks', { params }),
  getById: (id: string) => api.get(`/tasks/${id}`),
  create: (data: any) => api.post('/tasks', data),
  update: (id: string, data: any) => api.patch(`/tasks/${id}`, data),
  delete: (id: string) => api.delete(`/tasks/${id}`),
  complete: (id: string, data?: any) => api.post(`/tasks/${id}/complete`, data),
};

// ============================================================================
// Party API
// ============================================================================

export const partiesApi = {
  getAll: (params?: Record<string, any>) => api.get('/parties', { params }),
  getById: (id: string) => api.get(`/parties/${id}`),
  create: (data: any) => api.post('/parties', data),
  update: (id: string, data: any) => api.patch(`/parties/${id}`, data),
  delete: (id: string) => api.delete(`/parties/${id}`),
};

export default api;
