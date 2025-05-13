import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['STHeiti', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
from data.market_data import MarketDataFetcher
from strategies.ma_cross_strategy import MACrossStrategy
import seaborn as sns

def plot_strategy_results(data: pd.DataFrame):
    """绘制策略结果"""
    plt.figure(figsize=(15, 10))
    
    # 绘制价格和移动平均线
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['Close'], label='价格')
    plt.plot(data.index, data['short_ma'], label=f'短期MA({strategy.short_window})')
    plt.plot(data.index, data['long_ma'], label=f'长期MA({strategy.long_window})')
    
    # 标记买入卖出点
    buy_signals = data[data['position'] == 1.0]
    sell_signals = data[data['position'] == -1.0]
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='买入信号')
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='卖出信号')
    
    plt.title('移动平均线交叉策略')
    plt.legend()
    plt.grid(True)
    
    # 绘制资产曲线
    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['total'], label='总资产')
    plt.title('策略收益曲线')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # 设置绘图风格
    sns.set_style('darkgrid')
    
    # 获取数据
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_stock_data('TSLA', '2022-03-01', '2025-02-28')
    
    if data is not None:
        # 创建策略实例
        strategy = MACrossStrategy(short_window=20, long_window=50)
        
        # 回测策略
        total_return, annual_return, max_drawdown = strategy.backtest(data)
        
        # 打印结果
        print(f"\n策略回测结果:")
        print(f"总收益率: {total_return:.2%}")
        print(f"年化收益率: {annual_return:.2%}")
        print(f"最大回撤: {max_drawdown:.2%}")
        
        # 绘制结果
        plot_strategy_results(data)
    else:
        print("获取数据失败") 