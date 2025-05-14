import { api } from '../config/api';

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

export const marketDataService = {
  // 获取历史数据
  async getHistoricalData(params: HistoricalDataParams): Promise<HistoricalData> {
    try {
      const response = await api.get('/api/market_data/historical', { params });
      return response.data;
    } catch (error) {
      console.error('获取历史数据失败:', error);
      throw error;
    }
  },
}; 