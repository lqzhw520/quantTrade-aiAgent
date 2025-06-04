import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """市场数据获取类 - 使用 AKShare 作为数据源"""
    
    def __init__(self, max_retries=3, retry_delay=1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.data = None
    
    def fetch_stock_data(self, symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码 (如: '000001', '600000')
            start_date: 开始日期 (格式: 'YYYY-MM-DD' 或 'YYYYMMDD')
            end_date: 结束日期，默认为今天 (格式: 'YYYY-MM-DD' 或 'YYYYMMDD')
        
        Returns:
            DataFrame: 包含历史数据的DataFrame，列名包括 Date, Open, High, Low, Close, Volume
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 转换日期格式为 AKShare 需要的格式 (YYYYMMDD)
            if '-' in start_date:
                start_date = start_date.replace('-', '')
            if '-' in end_date:
                end_date = end_date.replace('-', '')
            
            logger.info(f"正在获取 {symbol} 从 {start_date} 到 {end_date} 的数据")
            
            for attempt in range(self.max_retries):
                try:
                    # 使用 AKShare 获取股票历史数据
                    # 只取前6位数字作为股票代码
                    stock_code = symbol[:6] if len(symbol) > 6 else symbol
                    
                    df = ak.stock_zh_a_hist(
                        symbol=stock_code, 
                        period="daily", 
                        start_date=start_date, 
                        end_date=end_date, 
                        adjust="qfq"  # 前复权
                    )
                    
                    if df is None or df.empty:
                        logger.warning(f"未获取到 {symbol} 的数据")
                        return None
                    
                    # 转换列名以匹配原有接口
                    df = df.rename(columns={
                        '日期': 'Date',
                        '开盘': 'Open',
                        '收盘': 'Close',
                        '最高': 'High',
                        '最低': 'Low',
                        '成交量': 'Volume'
                    })
                    
                    # 设置日期索引
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                    
                    # 只保留需要的列
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                    
                    logger.info(f"成功获取 {len(df)} 条数据记录")
                    self.data = df
                    return df
                    
                except Exception as e:
                    logger.error(f"获取 {symbol} 数据失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"获取数据异常: {str(e)}")
            return None
    
    def fetch_latest_price(self, symbol: str) -> dict:
        """
        获取股票最新价格
        
        Args:
            symbol: 股票代码 (如: '000001', '600000')
        
        Returns:
            dict: 包含最新价格信息的字典，如果获取失败返回 None
        """
        try:
            # 只取前6位数字作为股票代码
            stock_code = symbol[:6] if len(symbol) > 6 else symbol
            
            # 获取实时行情数据 - 使用正确的AKShare API
            df = ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                logger.warning(f"未获取到实时行情数据")
                return None
            
            # 查找指定股票代码的数据
            stock_data = df[df['代码'] == stock_code]
            
            if stock_data.empty:
                logger.warning(f"未找到股票代码 {symbol} 的数据")
                return None
            
            # 提取最新价格信息
            latest_price = {
                'symbol': symbol,
                'price': float(stock_data['最新价'].iloc[0]),
                'change': float(stock_data['涨跌额'].iloc[0]),
                'change_percent': float(stock_data['涨跌幅'].iloc[0]),
                'volume': int(stock_data['成交量'].iloc[0]),
                'timestamp': datetime.now().isoformat()
            }
            
            return latest_price
            
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