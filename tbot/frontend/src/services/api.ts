// tbot/frontend/src/services/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // FastAPI server address
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
