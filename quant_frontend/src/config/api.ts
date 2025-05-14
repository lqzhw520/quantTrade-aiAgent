import axios from 'axios';

// API 基础配置 - 自动检测后端地址
// 与 WebSocket 配置保持一致
const getApiBaseUrl = () => {
  // 如果是生产环境，使用相同的主机名，只改变端口
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${window.location.hostname}:5002`;
  }
  
  // 默认后端地址
  return 'http://localhost:5002';
};

export const API_BASE_URL = getApiBaseUrl();
console.log('使用 API 地址:', API_BASE_URL);

// 创建 axios 实例
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 统一错误处理
    console.error('API Error:', error);
    return Promise.reject(error);
  }
); 