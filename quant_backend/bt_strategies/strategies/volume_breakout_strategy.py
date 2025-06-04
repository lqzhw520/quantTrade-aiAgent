import backtrader as bt
import numpy as np
from datetime import datetime

class VolumeBreakoutStrategy(bt.Strategy):
    """
    交易量突破策略
    
    参数:
        volume_window: 交易量移动平均窗口周期
        volume_mult: 交易量放大倍数阈值
        price_change_threshold: 价格变化触发阈值(%)
        lookback_days: 价格对比的回看天数
    """
    params = (
        ('volume_window', 20),           # 成交量移动平均窗口
        ('volume_mult', 2.0),            # 放量倍数
        ('price_change_threshold', 2.0), # 价格变化阈值(%)
        ('lookback_days', 3),            # 回看天数
        ('order_percentage', 0.95),      # 订单金额占总资金比例
        ('printlog', False),             # 是否打印日志
    )
    
    def __init__(self):
        """初始化策略"""
        # 初始化指标
        self.dataclose = self.datas[0].close  # 收盘价
        self.datavolume = self.datas[0].volume  # 成交量
        
        # 创建交易量移动平均线
        self.volume_ma = bt.indicators.SMA(self.datavolume, period=self.params.volume_window)
        
        # 价格变化百分比
        self.price_change = bt.indicators.PercentChange(self.dataclose, period=self.params.lookback_days)
        
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
        
        # 计算交易量倍数
        current_volume = self.datavolume[0]
        volume_ratio = current_volume / self.volume_ma[0] if self.volume_ma[0] > 0 else 0
        
        # 获取价格变化百分比
        price_change_pct = self.price_change[0] * 100  # 转为百分比
        
        # 打印调试信息
        self.log(f'当前价格={self.dataclose[0]:.2f}, 交易量倍数={volume_ratio:.2f}, 价格变化={price_change_pct:.2f}%')
        
        # 交易逻辑
        if not self.position:  # 未持仓
            # 交易量大于均线的n倍 且 价格上涨超过阈值
            if (volume_ratio > self.params.volume_mult and 
                price_change_pct > self.params.price_change_threshold):
                # 计算购买数量
                available_cash = self.broker.getcash() * self.params.order_percentage
                size = int(available_cash / self.dataclose[0])
                
                if size > 0:
                    self.log(f'买入信号: 价格={self.dataclose[0]:.2f}, 交易量倍数={volume_ratio:.2f}, 价格变化={price_change_pct:.2f}%')
                    self.order = self.buy(size=size)
        else:  # 已持仓
            # 交易量大于均线的n倍 且 价格下跌超过阈值
            if (volume_ratio > self.params.volume_mult and 
                price_change_pct < -self.params.price_change_threshold):
                self.log(f'卖出信号: 价格={self.dataclose[0]:.2f}, 交易量倍数={volume_ratio:.2f}, 价格变化={price_change_pct:.2f}%')
                self.order = self.sell()
    
    def stop(self):
        """策略结束时调用"""
        # 输出最终结果
        self.log(f'(交易量窗口 {self.params.volume_window}) (放量倍数阈值 {self.params.volume_mult}) (价格变化阈值 {self.params.price_change_threshold}%)', doprint=True)
        self.log(f'期末资产: {self.broker.getvalue():.2f}', doprint=True)
    
    def get_signals(self):
        """获取交易信号"""
        return {
            'buy_signals': self.buy_signals,
            'sell_signals': self.sell_signals
        } 