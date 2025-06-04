import importlib.util
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Type

# 检查backtrader是否已安装
try:
    import backtrader as bt
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False

# 引入内部模块
from quant_backend.bt_strategies.bt_result_parser import BacktraderResultParser
from quant_backend.bt_strategies.strategies.ma_cross_strategy import MaCrossStrategy
from quant_backend.bt_strategies.strategies.volume_breakout_strategy import VolumeBreakoutStrategy

# 配置日志
logger = logging.getLogger(__name__)

def check_backtrader_installed():
    """检查backtrader是否已安装"""
    if not BACKTRADER_AVAILABLE:
        error_msg = (
            "Backtrader未安装。请运行以下命令安装:\n"
            "pip install backtrader\n"
            "pip install matplotlib==3.2.2  # Backtrader可能与最新版matplotlib不兼容"
        )
        logger.error(error_msg)
        raise ImportError(error_msg)

def prepare_data(
    df: pd.DataFrame, 
    date_col: str = 'trade_date',
    timestamp_col: Optional[str] = 'trade_time',
    price_cols: List[str] = ['open', 'high', 'low', 'close'],
    volume_col: str = 'vol'
) -> pd.DataFrame:
    """
    准备回测数据，标准化DataFrame格式
    
    参数:
        df: 输入数据DataFrame
        date_col: 日期列名
        timestamp_col: 时间戳列名，如果有
        price_cols: 价格列名列表 [open, high, low, close]
        volume_col: 成交量列名
        
    返回:
        标准化的DataFrame
    """
    df = df.copy()
    
    # 统一列名为小写
    df.columns = df.columns.str.lower()
    
    # 确保日期格式正确
    if date_col in df.columns:
        # 将字符串日期转换为日期时间对象
        if df[date_col].dtype == 'object' or df[date_col].dtype == 'str':
            try:
                # 尝试转换不同格式的日期
                df[date_col] = pd.to_datetime(df[date_col], format='%Y%m%d', errors='coerce')
                # 处理可能的NaT值
                if df[date_col].isna().any():
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            except Exception as e:
                logger.warning(f"日期转换错误: {str(e)}, 尝试使用pandas自动转换")
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # 设置日期索引
    if timestamp_col and timestamp_col in df.columns:
        # 如果有时间戳列，使用时间戳作为索引
        df['datetime'] = pd.to_datetime(df[timestamp_col], errors='coerce')
        df.set_index('datetime', inplace=True)
    elif date_col in df.columns:
        # 如果只有日期列，使用日期作为索引
        if 'datetime' not in df.columns:
            df['datetime'] = pd.to_datetime(df[date_col], errors='coerce')
        df.set_index('datetime', inplace=True)
    
    # 确保索引是日期时间格式
    if not isinstance(df.index, pd.DatetimeIndex):
        logger.warning("无法将索引转换为DatetimeIndex，将创建默认索引")
        df.reset_index(inplace=True)
        df['datetime'] = pd.date_range(start='2000-01-01', periods=len(df), freq='D')
        df.set_index('datetime', inplace=True)
    
    # 重命名成交量列
    if volume_col in df.columns and volume_col != 'volume':
        df['volume'] = df[volume_col]
    
    # 确保所有价格列存在
    for col in ['open', 'high', 'low', 'close']:
        if col not in df.columns:
            df[col] = df['close'] if 'close' in df.columns else 0.0
    
    # 确保所有数值列是浮点类型
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # 处理可能的缺失数据，确保连续性
    df = df.sort_index()
    df = df.ffill()  # 使用新的前向填充方法
    
    # 移除重复索引
    df = df[~df.index.duplicated(keep='first')]
    
    return df

def get_strategy_class(strategy_name: str) -> Type[bt.Strategy]:
    """
    根据策略名称获取策略类
    
    参数:
        strategy_name: 策略名称
        
    返回:
        对应的策略类
    """
    # 策略映射表
    strategies = {
        'ma_cross': MaCrossStrategy,
        'volume_breakout': VolumeBreakoutStrategy
    }
    
    # 尝试从映射表获取策略类
    if strategy_name in strategies:
        return strategies[strategy_name]
    
    # 如果找不到，尝试动态导入
    try:
        module_path = f"quant_backend.bt_strategies.strategies.{strategy_name}"
        strategy_module = importlib.import_module(module_path)
        
        # 尝试找到与文件名匹配的类
        class_name = ''.join(word.capitalize() for word in strategy_name.split('_'))
        strategy_class = getattr(strategy_module, class_name)
        
        return strategy_class
    except (ImportError, AttributeError) as e:
        logger.error(f"找不到策略: {strategy_name}, 错误: {str(e)}")
        # 默认使用MaCrossStrategy
        return MaCrossStrategy

def run_backtest(
    df: pd.DataFrame,
    strategy_name: str = 'ma_cross',
    strategy_params: Optional[Dict[str, Any]] = None,
    initial_capital: float = 100000.0,
    commission: float = 0.001
) -> Dict[str, Any]:
    """
    运行回测主函数
    
    参数:
        df: 包含OHLCV数据的DataFrame
        strategy_name: 策略名称
        strategy_params: 策略参数字典
        initial_capital: 初始资金
        commission: 交易佣金比例
        
    返回:
        回测结果字典
    """
    # 检查backtrader是否已安装
    check_backtrader_installed()
    
    # 准备数据
    data = prepare_data(df)
    
    # 创建cerebro引擎
    cerebro = bt.Cerebro()
    
    # 获取策略类
    strategy_class = get_strategy_class(strategy_name)
    
    # 添加策略
    if strategy_params:
        cerebro.addstrategy(strategy_class, **strategy_params)
    else:
        cerebro.addstrategy(strategy_class)
    
    # 正确配置PandasData
    bt_data = bt.feeds.PandasData(
        dataname=data,
        datetime=None,  # 使用索引作为日期时间
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    
    # 添加数据源
    cerebro.adddata(bt_data)
    
    # 设置初始资金和佣金
    cerebro.broker.setcash(initial_capital)
    cerebro.broker.setcommission(commission=commission)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade')
    
    # 运行回测
    logger.info(f'开始回测，初始资金: {initial_capital:.2f}')
    results = cerebro.run()
    strategy_instance = results[0]
    
    # 获取最终资金
    final_value = cerebro.broker.getvalue()
    logger.info(f'回测完成，最终资金: {final_value:.2f}')
    
    # 解析并返回结果
    return BacktraderResultParser.parse_results(
        cerebro, strategy_instance, data, initial_capital
    )
