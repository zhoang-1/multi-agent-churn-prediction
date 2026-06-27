import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const customerApi = {
  // Uses /api/data
  getData: async (query) => {
    // query could be { phone: '123' } or { email: 'a@b.c' }
    const response = await api.post('/data', query);
    return response.data;
  },
  getSentiment: async (query) => {
    const response = await api.post('/sentiment', query);
    return response.data;
  },
  getChurn: async (query) => {
    const response = await api.post('/churn', query);
    return response.data;
  },
  getReport: async (query) => {
    const response = await api.post('/report', query);
    return response.data;
  },
  getPipeline: async (query) => {
    const response = await api.post('/pipeline', query);
    return response.data;
  }
};

export default api;
