from flask import Blueprint, request, jsonify
from quant_backend.services.strategy_service import MACrossStrategy
import yfinance as yf
import pandas as pd

strategy_bp = Blueprint('strategy', __name__, url_prefix='/api/strategy')

@strategy_bp.route('/backtest', methods=['POST'])
def backtest():
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = float(data.get('initial_capital', 100000))
        short_window = int(data.get('short_window', 20))
        long_window = int(data.get('long_window', 50))

        # 获取历史数据
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return jsonify({'error': '无法获取历史数据'}), 400

        # 执行回测
        strategy = MACrossStrategy(short_window=short_window, long_window=long_window)
        results = strategy.backtest(hist, initial_capital=initial_capital)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 