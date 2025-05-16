import os
import logging
import tushare as ts
import pandas as pd
from typing import List, Dict, Any, Optional

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

# 官方推荐初始化方式
TS_TOKEN = '2abb38fa6b00dde66bea48baff0477f13d35d67cbaef1c443c6eae63'
pro = ts.pro_api(TS_TOKEN)
logger.info('Tushare Pro 初始化成功。')

def check_tushare_permission():
    try:
        df = pro.query('api_permission', fields='api_name,is_granted')
        granted = df[df['is_granted'] == 1]['api_name'].tolist()
        logger.info(f'当前账号已开通接口: {granted}')
        return granted
    except Exception as e:
        logger.error(f'检查Tushare接口权限失败: {e}')
        return []

def get_stock_list() -> Optional[List[Dict[str, Any]]]:
    """
    获取最新的 A 股股票列表。
    返回包含股票代码（ts_code）和股票名称（name）的字典列表。
    :return: List[Dict[str, Any]] 或 None（出错时）
    """
    if pro is None:
        logger.error('Tushare Pro 未初始化，无法获取股票列表。')
        return None
    try:
        # 获取A股上市公司列表
        df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
        stock_list = df.to_dict(orient='records')
        logger.info(f'成功获取A股股票列表，共 {len(stock_list)} 条。')
        return stock_list
    except Exception as e:
        logger.error(f'获取A股股票列表失败: {e}')
        return None 

def get_stock_historical_data(ts_code: str, period: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    获取指定股票的历史行情数据。
    :param ts_code: 股票代码（如 '000001.SZ'）
    :param period: 数据周期，'daily'（日线）、'weekly'（周线）、'monthly'（月线）
    :param start_date: 开始日期，格式 YYYYMMDD
    :param end_date: 结束日期，格式 YYYYMMDD
    :return: 包含行情数据的 DataFrame 或 None（出错时）
    """
    if pro is None:
        logger.error('Tushare Pro 未初始化，无法获取历史行情数据。')
        return None
    period_map = {
        'daily': 'daily',
        'weekly': 'weekly',
        'monthly': 'monthly',
    }
    tushare_func_map = {
        'daily': pro.daily,
        'weekly': pro.weekly,
        'monthly': pro.monthly,
    }
    if period not in period_map:
        logger.error(f'不支持的周期类型: {period}')
        return None
    try:
        func = tushare_func_map[period]
        df = func(ts_code=ts_code, start_date=start_date, end_date=end_date,
                  fields="ts_code,trade_date,open,high,low,close,vol,amount")
        if df is None or df.empty:
            logger.warning(f'未获取到行情数据: {ts_code}, {period}, {start_date}-{end_date}')
            return None
        # 按日期升序排列
        df = df.sort_values('trade_date')
        logger.info(f'成功获取{ts_code} {period} 行情数据 {len(df)} 条。')
        return df
    except Exception as e:
        logger.error(f'获取{ts_code} {period} 行情数据失败: {e}')
        return None 