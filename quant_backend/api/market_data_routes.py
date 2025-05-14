from flask import Blueprint, request, jsonify
from ..services.market_data_service import MarketDataFetcher

market_data_bp = Blueprint('market_data', __name__, url_prefix='/api/market_data')

@market_data_bp.route('/historical', methods=['GET'])
def get_historical_data():
    try:
        symbol = request.args.get('symbol')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not all([symbol, start_date, end_date]):
            return jsonify({'error': '缺少必要参数'}), 400

        fetcher = MarketDataFetcher()
        data = fetcher.fetch_stock_data(symbol, start_date, end_date)
        
        if data is None or data.empty:
            return jsonify({'error': '未获取到数据'}), 404

        return jsonify({
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'close_prices': data['Close'].round(2).tolist(),
            'volumes': data['Volume'].tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_data_bp.route('/latest_price', methods=['GET'])
def get_latest_price():
    try:
        symbol = request.args.get('symbol')
        if not symbol:
            return jsonify({'error': '缺少股票代码'}), 400

        fetcher = MarketDataFetcher()
        price = fetcher.fetch_latest_price(symbol)
        
        if price is None:
            return jsonify({'error': '未获取到价格数据'}), 404

        return jsonify(price)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 