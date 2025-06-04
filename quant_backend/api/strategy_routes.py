from flask import Blueprint, request, jsonify
from quant_backend.services.strategy_service import MACrossStrategy
from quant_backend.services import akshare_service
import pandas as pd
import logging
from datetime import datetime, timedelta

# 引入Backtrader回测模块
try:
    from quant_backend.bt_strategies.backtest_runner import run_backtest, check_backtrader_installed
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False

logger = logging.getLogger(__name__)
strategy_bp = Blueprint('strategy', __name__, url_prefix='/api/strategy')

@strategy_bp.route('/backtest', methods=['POST'])
def backtest():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
            
        # 必要参数验证
        required_fields = ['symbol', 'start_date', 'end_date', 'initial_capital', 'short_window', 'long_window']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必要参数: {", ".join(missing_fields)}'}), 400

        symbol = data.get('symbol')  # 应该是类似 '000001.SZ' 格式
        start_date = data.get('start_date')  # 格式：YYYY-MM-DD
        end_date = data.get('end_date')
        initial_capital = float(data.get('initial_capital', 100000))
        short_window = int(data.get('short_window', 20))
        long_window = int(data.get('long_window', 50))

        # 参数有效性验证
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                return jsonify({'error': '开始日期不能晚于结束日期'}), 400
            if end > datetime.now():
                return jsonify({'error': '结束日期不能晚于今天'}), 400
        except ValueError:
            return jsonify({'error': '日期格式无效，应为 YYYY-MM-DD'}), 400

        if short_window >= long_window:
            return jsonify({'error': '短期窗口必须小于长期窗口'}), 400

        if initial_capital <= 0:
            return jsonify({'error': '初始资金必须大于0'}), 400

        # 使用 AKShare 获取历史数据
        logger.info(f'获取股票数据: {symbol}, {start_date} -> {end_date}')
        try:
            # 转换日期格式为 YYYYMMDD
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            # 向前多取一些数据，确保有足够数据计算指标
            fetch_start = (start - timedelta(days=long_window * 2)).strftime('%Y%m%d')
            hist_data = akshare_service.get_stock_historical_data(
                ts_code=symbol,
                period='daily',
                start_date=fetch_start,
                end_date=end_date_fmt
            )
            
            if hist_data is None or hist_data.empty:
                return jsonify({'error': f'无法获取 {symbol} 的历史数据'}), 400

            # 转换数据格式以适配策略
            hist = pd.DataFrame({
                'Open': hist_data['open'],
                'High': hist_data['high'],
                'Low': hist_data['low'],
                'Close': hist_data['close'],
                'Volume': hist_data['vol']
            }, index=pd.to_datetime(hist_data['trade_date'], format='%Y%m%d'))

            # 确保数据充足
            if len(hist) < long_window * 2:
                return jsonify({'error': f'历史数据不足，至少需要 {long_window * 2} 个交易日'}), 400

            # 执行回测
            strategy = MACrossStrategy(short_window=short_window, long_window=long_window)
            results = strategy.backtest(hist, initial_capital=initial_capital)
            
            logger.info(f'回测完成: {symbol}, 总收益率: {results["performance"]["total_return"]:.2%}')
            return jsonify(results)
            
        except Exception as e:
            logger.error(f'获取历史数据失败: {str(e)}', exc_info=True)
            return jsonify({'error': f'获取历史数据失败: {str(e)}'}), 400
            
    except Exception as e:
        logger.error(f'回测执行异常: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@strategy_bp.route('/backtest_bt', methods=['POST'])
def backtest_bt():
    """
    使用Backtrader进行回测的API接口
    
    请求参数:
        symbol: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        strategy_name: 策略名称, 默认为 'ma_cross'
        initial_capital: 初始资金, 默认为 100000
        short_window: 短期移动平均线周期 (对于MaCrossStrategy)
        long_window: 长期移动平均线周期 (对于MaCrossStrategy)
        
    返回:
        回测结果字典，包含绩效指标和图表数据
    """
    try:
        # 检查Backtrader是否可用
        if not BACKTRADER_AVAILABLE:
            return jsonify({
                'error': '未安装Backtrader。请运行: pip install backtrader matplotlib==3.2.2'
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 必要参数验证
        required_fields = ['symbol', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'缺少必要参数: {", ".join(missing_fields)}'}), 400
        
        # 提取参数
        symbol = data.get('symbol')
        start_date = data.get('start_date')  # 格式：YYYY-MM-DD
        end_date = data.get('end_date')  # 格式：YYYY-MM-DD
        strategy_name = data.get('strategy_name', 'ma_cross')
        initial_capital = float(data.get('initial_capital', 100000.0))
        
        # 构造策略参数
        strategy_params = {}
        if strategy_name == 'ma_cross':
            strategy_params['short_ma'] = int(data.get('short_window', 20))
            strategy_params['long_ma'] = int(data.get('long_window', 50))
            
            # 参数有效性验证
            if strategy_params['short_ma'] >= strategy_params['long_ma']:
                return jsonify({'error': '短期窗口必须小于长期窗口'}), 400
        
        # 日期有效性验证
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                return jsonify({'error': '开始日期不能晚于结束日期'}), 400
            if end > datetime.now():
                return jsonify({'error': '结束日期不能晚于今天'}), 400
        except ValueError:
            return jsonify({'error': '日期格式无效，应为 YYYY-MM-DD'}), 400
        
        # 使用 AKShare 获取历史数据
        logger.info(f'获取股票数据 (Backtrader): {symbol}, {start_date} -> {end_date}')
        
        try:
            # 转换日期格式
            start_date_fmt = start_date.replace('-', '')
            end_date_fmt = end_date.replace('-', '')
            
            # 向前多取一些数据，确保有足够数据计算指标
            fetch_start = (start - timedelta(days=strategy_params.get('long_ma', 60) * 2)).strftime('%Y%m%d')
            
            # 获取历史数据
            hist_data = akshare_service.get_stock_historical_data(
                ts_code=symbol,
                period='daily',
                start_date=fetch_start,
                end_date=end_date_fmt
            )
            
            if hist_data is None or hist_data.empty:
                return jsonify({'error': f'无法获取 {symbol} 的历史数据'}), 400
            
            # 运行Backtrader回测
            results = run_backtest(
                df=hist_data,
                strategy_name=strategy_name,
                strategy_params=strategy_params,
                initial_capital=initial_capital
            )
            
            logger.info(f'Backtrader回测完成: {symbol}, 策略: {strategy_name}')
            return jsonify(results)
            
        except Exception as e:
            logger.error(f'Backtrader回测失败: {str(e)}', exc_info=True)
            return jsonify({'error': f'回测执行失败: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f'Backtrader API异常: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500 