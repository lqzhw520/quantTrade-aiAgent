from flask import Blueprint, request, jsonify
from quant_backend.services.strategy_service import MACrossStrategy
from quant_backend.services import akshare_service
import pandas as pd
import logging
from datetime import datetime, timedelta

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