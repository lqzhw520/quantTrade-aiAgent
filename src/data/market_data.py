import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """市场数据获取类"""
    
    def __init__(self):
        self.data = None
    
    def fetch_stock_data(self, symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期，默认为当前日期
            
        Returns:
            DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            logger.info(f"正在获取 {symbol} 从 {start_date} 到 {end_date} 的数据")
            stock = yf.Ticker(symbol)
            self.data = stock.history(start=start_date, end=end_date)
            
            if self.data.empty:
                logger.warning(f"未获取到 {symbol} 的数据")
                return None
                
            logger.info(f"成功获取 {len(self.data)} 条数据记录")
            return self.data
            
        except Exception as e:
            logger.error(f"获取数据时发生错误: {str(e)}")
            return None
    
    def get_latest_price(self, symbol: str) -> float:
        """
        获取最新价格
        
        Args:
            symbol: 股票代码
            
        Returns:
            float: 最新价格
        """
        try:
            stock = yf.Ticker(symbol)
            latest_data = stock.history(period='1d')
            if not latest_data.empty:
                return latest_data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"获取最新价格时发生错误: {str(e)}")
            return None
    
    def get_data_info(self) -> dict:
        """
        获取数据基本信息
        
        Returns:
            dict: 包含数据基本信息的字典
        """
        if self.data is None:
            return None
            
        return {
            '数据条数': len(self.data),
            '时间范围': f"{self.data.index[0]} 到 {self.data.index[-1]}",
            '列名': list(self.data.columns),
            '数据类型': self.data.dtypes.to_dict()
        } 