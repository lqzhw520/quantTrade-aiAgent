import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest
import json
import os
import sys

# 检查backtrader是否已安装
try:
    import backtrader as bt
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 有条件地导入回测模块
if BACKTRADER_AVAILABLE:
    from quant_backend.bt_strategies.backtest_runner import run_backtest, prepare_data, get_strategy_class
    from quant_backend.bt_strategies.strategies.ma_cross_strategy import MaCrossStrategy
    from quant_backend.bt_strategies.bt_result_parser import BacktraderResultParser

# 创建测试数据
def create_test_data():
    """创建用于测试的模拟股票数据"""
    # 创建日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 设置初始价格和波动范围
    initial_price = 100
    price_std = 2.0
    
    # 生成随机价格
    close_prices = np.random.normal(initial_price, price_std, len(dates))
    # 确保价格有一定的趋势性
    trend = np.linspace(0, 20, len(dates))
    close_prices = close_prices + trend
    
    # 生成其他价格列和成交量
    open_prices = close_prices + np.random.normal(0, 1, len(dates))
    high_prices = np.maximum(close_prices, open_prices) + abs(np.random.normal(0, 1, len(dates)))
    low_prices = np.minimum(close_prices, open_prices) - abs(np.random.normal(0, 1, len(dates)))
    volumes = np.random.randint(1000, 100000, len(dates))
    
    # 创建DataFrame
    df = pd.DataFrame({
        'trade_date': dates.strftime('%Y%m%d'),  # 直接转换为字符串格式，避免NaT问题
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'vol': volumes
    })
    
    # 确保所有数值都是有效的（去掉NaN和无穷值）
    for col in ['open', 'high', 'low', 'close', 'vol']:
        df[col] = df[col].fillna(100.0)  # 用合理默认值填充
        df[col] = df[col].replace([np.inf, -np.inf], 100.0)  # 替换无穷值
    
    return df

# 标记仅在backtrader可用时运行的测试
backtrader_required = pytest.mark.skipif(
    not BACKTRADER_AVAILABLE,
    reason="Backtrader not installed"
)

@backtrader_required
class TestBacktestRunner(unittest.TestCase):
    """测试Backtrader回测功能"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建测试数据
        self.test_data = create_test_data()
    
    def test_prepare_data(self):
        """测试数据准备函数"""
        # 准备数据
        prepared_data = prepare_data(self.test_data)
        
        # 检查结果
        self.assertIsInstance(prepared_data, pd.DataFrame)
        self.assertIsInstance(prepared_data.index, pd.DatetimeIndex)
        
        # 检查必要的列
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertIn(col, prepared_data.columns)
    
    def test_get_strategy_class(self):
        """测试策略类获取函数"""
        # 获取已知策略
        strategy_class = get_strategy_class('ma_cross')
        self.assertEqual(strategy_class, MaCrossStrategy)
        
        # 获取未知策略，应该返回默认策略
        strategy_class = get_strategy_class('unknown_strategy')
        self.assertEqual(strategy_class, MaCrossStrategy)
    
    def test_run_backtest(self):
        """测试回测执行函数"""
        try:
            # 运行回测
            results = run_backtest(
                df=self.test_data,
                strategy_name='ma_cross',
                strategy_params={'short_ma': 10, 'long_ma': 30},
                initial_capital=100000.0
            )
            
            # 检查结果结构
            self.assertIsInstance(results, dict)
            self.assertIn('performance', results)
            self.assertIn('chart_data', results)
            
            # 检查绩效指标
            performance = results['performance']
            for metric in ['total_return', 'annual_return', 'max_drawdown', 'sharpe_ratio']:
                self.assertIn(metric, performance)
                self.assertIsInstance(performance[metric], float)
            
            # 检查图表数据
            chart_data = results['chart_data']
            for key in ['dates', 'close_prices', 'short_ma', 'long_ma']:
                self.assertIn(key, chart_data)
                self.assertIsInstance(chart_data[key], list)
            
            # 检查交易信号
            for signal_type in ['buy_signals', 'sell_signals']:
                self.assertIn(signal_type, chart_data)
                self.assertIsInstance(chart_data[signal_type], list)
                
                # 如果有信号，检查信号格式
                if chart_data[signal_type]:
                    signal = chart_data[signal_type][0]
                    self.assertIn('date', signal)
                    self.assertIn('price', signal)
        except Exception as e:
            self.fail(f"回测执行失败: {str(e)}")

@pytest.mark.skipif(not BACKTRADER_AVAILABLE, reason="Backtrader not installed")
def test_backtest_result_serialization():
    """测试回测结果是否可以正确序列化为JSON"""
    # 创建测试数据
    test_data = create_test_data()
    
    try:
        # 运行回测
        results = run_backtest(
            df=test_data,
            strategy_name='ma_cross',
            strategy_params={'short_ma': 10, 'long_ma': 30},
            initial_capital=100000.0
        )
        
        # 尝试JSON序列化
        json_data = json.dumps(results)
        assert isinstance(json_data, str)
        
        # 反序列化并验证结构完整性
        parsed_data = json.loads(json_data)
        assert 'performance' in parsed_data
        assert 'chart_data' in parsed_data
    except Exception as e:
        pytest.fail(f"结果序列化失败: {str(e)}")

if __name__ == '__main__':
    if BACKTRADER_AVAILABLE:
        unittest.main()
    else:
        print("Backtrader未安装，无法运行测试。请先安装: pip install backtrader matplotlib==3.2.2")
