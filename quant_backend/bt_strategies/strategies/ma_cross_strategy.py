import backtrader as bt
import numpy as np
import pandas as pd
from datetime import datetime

class MaCrossStrategy(bt.Strategy):
    """
    简单移动平均线交叉策略
    
    参数:
        short_ma: 短期移动平均线周期
        long_ma: 长期移动平均线周期
    """
    params = (
        ('short_ma', 20),  # 短期移动平均线周期
        ('long_ma', 60),   # 长期移动平均线周期
        ('printlog', False),  # 是否打印日志
    )
    
    def __init__(self):
        """初始化策略"""
        # 初始化指标
        self.dataclose = self.datas[0].close  # 收盘价
        
        # 创建移动平均线指标
        self.short_ma = bt.indicators.SMA(self.dataclose, period=self.params.short_ma)
        self.long_ma = bt.indicators.SMA(self.dataclose, period=self.params.long_ma)
        
        # 创建交叉信号指标
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)
        
        # 交易状态
        self.order = None  # 当前挂单
        self.buy_price = None  # 买入价格
        self.buy_comm = None   # 买入佣金
        
        # 存储交易信号
        self.buy_signals = []  # 买入信号
        self.sell_signals = [] # 卖出信号
        
    def log(self, txt, dt=None, doprint=False):
        """记录策略日志"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        """处理订单状态"""
        # 如果订单已提交或已接受，不做任何事
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        # 检查订单是否已完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行: 价格={order.executed.price:.2f}, 成本={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                # 记录买入信号
                self.buy_signals.append({
                    'date': self.datas[0].datetime.date(0).isoformat(),
                    'price': order.executed.price
                })
            else:  # 卖出
                self.log(f'卖出执行: 价格={order.executed.price:.2f}, 成本={order.executed.value:.2f}, 佣金={order.executed.comm:.2f}')
                # 记录卖出信号
                self.sell_signals.append({
                    'date': self.datas[0].datetime.date(0).isoformat(),
                    'price': order.executed.price
                })
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单被取消/拒绝')
        
        # 重置订单
        self.order = None
    
    def notify_trade(self, trade):
        """处理交易结果"""
        if not trade.isclosed:
            return
        
        self.log(f'交易利润: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
    
    def next(self):
        """每个bar调用一次的主策略方法"""
        # 如果有挂单，不执行新的交易
        if self.order:
            return
        
        # 是否持仓
        if not self.position:
            # 如果短期均线上穿长期均线，买入
            if self.crossover > 0:
                self.log(f'买入信号: 价格={self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            # 如果短期均线下穿长期均线，卖出
            if self.crossover < 0:
                self.log(f'卖出信号: 价格={self.dataclose[0]:.2f}')
                self.order = self.sell()
    
    def stop(self):
        """策略结束时调用"""
        # 输出最终结果
        self.log(f'(短期周期 {self.params.short_ma}) (长期周期 {self.params.long_ma})', doprint=True)
        self.log(f'期末资产: {self.broker.getvalue():.2f}', doprint=True)
    
    def get_signals(self):
        """获取交易信号"""
        return {
            'buy_signals': self.buy_signals,
            'sell_signals': self.sell_signals
        }



