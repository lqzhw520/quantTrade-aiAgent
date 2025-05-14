import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """市场数据获取类"""
    
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.data = None
    
    def fetch_stock_data(self, symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期，默认为今天
        
        Returns:
            DataFrame: 包含历史数据的DataFrame
        """
        try:
            logger.info(f"正在获取 {symbol} 从 {start_date} 到 {end_date} 的数据")
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            logger.info(f"成功获取 {len(hist)} 条数据记录")
            return hist
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            return None
    
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"正在获取 {symbol} 从 {start_date} 到 {end_date} 的数据")
        
        for attempt in range(self.max_retries):
            try:
                # 使用 Ticker 对象获取数据
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if df is None or df.empty:
                    logger.warning(f"未获取到 {symbol} 的数据")
                    return None
                    
                logger.info(f"成功获取 {len(df)} 条数据记录")
                self.data = df
                return df
                
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
                
        return None
    
    def get_latest_price(self, symbol: str) -> float:
        """
        获取股票最新价格
        
        Args:
            symbol: 股票代码
        
        Returns:
            最新价格，如果获取失败返回 None
        """
        try:
            ticker = yf.Ticker(symbol)
            # 获取最近一天的数据
            df = ticker.history(period="1d")
            if df is None or df.empty:
                logger.warning(f"未获取到 {symbol} 的最新价格")
                return None
            return df['Close'].iloc[-1]
        except Exception as e:
            logger.error(f"获取 {symbol} 最新价格失败: {str(e)}")
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