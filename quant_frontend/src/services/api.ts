import axios from 'axios';

// 根据环境动态设置API基础URL
const getApiBaseUrl = () => {
  // 检查是否为生产环境
  const isProd = window.location.hostname !== 'localhost' && 
                window.location.hostname !== '127.0.0.1';
  
  // 生产环境使用相同域名下的API
  if (isProd && window.location.port === '') {
    return `${window.location.origin}/api`;
  }
  
  // 如果在其他网络环境运行，使用相同主机名但不同端口
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${window.location.hostname}:5002`;
  }
  
  // 本地开发环境
  return 'http://localhost:5002';
};

const API_BASE_URL = getApiBaseUrl();
console.log('使用API基础URL:', API_BASE_URL);

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息等
    // 添加请求时间戳，避免缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
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
    // 统一错误处理
    let errorMessage = '请求失败';
    
    if (error.response) {
      // 服务器返回了响应，但状态码不是2xx
      const status = error.response.status;
      const data = error.response.data;
      
      switch (status) {
        case 400:
          errorMessage = data.error || '请求参数错误';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器内部错误';
          break;
        default:
          errorMessage = `服务器错误 (${status})`;
      }
      
      console.error('API响应错误:', status, data);
    } else if (error.request) {
      // 请求已发送但没收到响应
      if (error.code === 'ECONNABORTED') {
        errorMessage = '请求超时，请检查网络连接';
      } else {
        errorMessage = '网络连接失败，无法联系服务器';
      }
      console.error('网络请求错误:', error.request);
    } else {
      // 请求配置出错
      errorMessage = error.message || '请求配置错误';
      console.error('请求配置错误:', error.message);
    }
    
    // 可以在这里添加全局错误通知
    
    return Promise.reject({
      ...error,
      message: errorMessage
    });
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
    sharpe_ratio?: number;
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

// 获取A股股票列表
export interface StockItem {
  ts_code: string;
  name: string;
}

export interface IndicatorParams {
  ts_code: string;
  period?: string;
  start_date: string;
  end_date: string;
  ma_windows?: string;   // 例如 "5,20,60"
  vma_windows?: string;  // 例如 "5"
}

export interface IndicatorResult {
  dates: string[];
  close: number[];
  volume: number[];
  obv: number[];
  vr: number[];
  mfi: number[];
  [key: string]: number[] | string[]; // 支持动态窗口如 vma_5, pma_20
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
    try {
      // 转换日期格式为 YYYY-MM-DD
      const formattedParams = {
        ...params,
        start_date: params.start_date.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'),
        end_date: params.end_date.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3')
      };
      
      console.log('发送回测请求，参数:', formattedParams);
      const { data } = await api.post<BacktestResult>('/api/strategy/backtest', formattedParams);
      return data;
    } catch (error: any) {
      console.error('回测执行失败:', error.message);
      throw error;
    }
  },

  // 获取股票列表
  getStockList: async (): Promise<StockItem[]> => {
    const res = await api.get('/api/market_data/stock_list');
    // 兼容后端返回 {data: [...]}
    if (res && Array.isArray(res.data)) {
      return res.data;
    }
    return [];
  },

  // 获取技术指标
  getIndicators: async (params: IndicatorParams): Promise<IndicatorResult> => {
    return api.get('/api/market_data/indicators', { params });
  }
}; 