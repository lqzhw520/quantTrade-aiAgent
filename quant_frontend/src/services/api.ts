import axios from 'axios';

const API_BASE_URL = 'http://localhost:5002';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息等
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API 接口定义
export interface HistoricalDataParams {
  symbol: string;
  start_date: string;
  end_date: string;
}

export interface HistoricalData {
  dates: string[];
  close_prices: number[];
  volumes: number[];
}

export interface BacktestParams {
  strategy_name: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  short_window: number;
  long_window: number;
}

export interface BacktestResult {
  performance: {
    total_return: number;
    annual_return: number;
    max_drawdown: number;
  };
  chart_data: {
    dates: string[];
    close_prices: number[];
    short_ma: number[];
    long_ma: number[];
    buy_signals: Array<{ date: string; price: number }>;
    sell_signals: Array<{ date: string; price: number }>;
    equity_curve: Array<{ date: string; value: number }>;
  };
}

// API 服务
export const apiService = {
  // 获取历史数据
  getHistoricalData: async (params: HistoricalDataParams): Promise<HistoricalData> => {
    return api.get('/api/market_data/historical', { params });
  },

  // 获取最新价格
  getLatestPrice: async (symbol: string): Promise<{ price: number; timestamp: string }> => {
    return api.get('/api/market_data/latest_price', { params: { symbol } });
  },

  // 执行回测
  runBacktest: async (params: BacktestParams): Promise<BacktestResult> => {
    return api.post('/api/strategy/backtest', params);
  }
}; 