// frontend/src/api/axiosConfig.js
import axios from 'axios';

// Create a custom instance of axios
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/', // Your Django API URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;