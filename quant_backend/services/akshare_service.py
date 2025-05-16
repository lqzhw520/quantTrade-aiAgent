import logging
import akshare as ak
import pandas as pd
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

def get_stock_list() -> Optional[List[Dict[str, Any]]]:
    """
    获取最新的 A 股股票列表。
    返回包含股票代码（ts_code）和股票名称（name）的字典列表。
    :return: List[Dict[str, Any]] 或 None（出错时）
    """
    df = ak.stock_info_a_code_name()
    # AKShare 字段: code, name
    df['ts_code'] = df['code'].apply(lambda x: f"{x[:6]}.SH" if x.startswith('6') else f"{x[:6]}.SZ")
    stock_list = df[['ts_code', 'name']].to_dict(orient='records')
    logger.info(f'成功获取A股股票列表，共 {len(stock_list)} 条。')
    return stock_list

def get_stock_historical_data(ts_code: str, period: str = 'daily', start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
    """
    获取指定股票的历史行情数据。
    :param ts_code: 股票代码（如 '000001.SZ'）
    :param period: 数据周期，'daily'（日线）、'weekly'（周线）、'monthly'（月线）
    :param start_date: 开始日期，格式 YYYYMMDD
    :param end_date: 结束日期，格式 YYYYMMDD
    :return: 包含行情数据的 DataFrame 或 None（出错时）
    """
    # 只取前6位数字
    code = ts_code[:6]
    period_map = {
        'daily': 'daily',
        'weekly': 'weekly',
        'monthly': 'monthly',
    }
    if not period or period not in period_map:
        logger.warning(f'period 参数非法({period})，自动设为 daily')
        raise ValueError(f'不支持的周期类型: {period}')
    try:
        df = ak.stock_zh_a_hist(symbol=code, period=period_map[period], start_date=start_date, end_date=end_date, adjust="qfq")
    except Exception as e:
        logger.error(f'调用 AKShare 获取行情异常: {e}, period={period}, ts_code={ts_code}, symbol={code}')
        raise RuntimeError(f'AKShare period参数异常: {e}, period={period}, ts_code={ts_code}, symbol={code}')
    if df is None or df.empty:
        logger.warning(f'未获取到行情数据: {ts_code}, {period}, {start_date}-{end_date}')
        return None
    # 字段适配
    df = df.rename(columns={
        '日期': 'trade_date',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'vol',
        '成交额': 'amount',
    })
    for col in ['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']:
        if col not in df.columns:
            df[col] = None
    df = df[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
    df = df.sort_values('trade_date')
    logger.info(f'成功获取{ts_code} {period} 行情数据 {len(df)} 条。')
    return df 