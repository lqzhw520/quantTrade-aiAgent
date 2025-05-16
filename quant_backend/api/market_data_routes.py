from flask import Blueprint, request, jsonify
from ..services.market_data_service import MarketDataFetcher
from ..services import akshare_service
from ..utils.technical_indicators import TechnicalIndicators
import numpy as np
import pandas as pd

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

@market_data_bp.route('/stock_list', methods=['GET'])
def get_stock_list():
    """
    获取最新A股股票列表（ts_code, name），返回JSON。
    """
    try:
        stock_list = akshare_service.get_stock_list()
        if stock_list is None:
            return jsonify({'error': '获取股票列表失败'}), 500
        return jsonify({'data': stock_list})
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'获取股票列表API异常: {e}')
        return jsonify({'error': str(e)}), 500

@market_data_bp.route('/historical_data', methods=['GET'])
def get_stock_historical_data_api():
    """
    获取指定股票的历史行情数据，支持日/周/月线。
    参数: ts_code, period, start_date, end_date
    返回: JSON 格式行情数据
    """
    try:
        ts_code = request.args.get('ts_code')
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if not all([ts_code, period, start_date, end_date]):
            return jsonify({'error': '缺少必要参数'}), 400
        try:
            df = akshare_service.get_stock_historical_data(ts_code, period, start_date, end_date)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f'获取历史行情API异常: {e}')
            return jsonify({'error': str(e)}), 500
        if df is None or df.empty:
            return jsonify({'error': '未获取到行情数据'}), 404
        # 只返回需要的字段
        data = df[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']].to_dict(orient='records')
        return jsonify({'data': data})
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'获取历史行情API异常: {e}')
        return jsonify({'error': str(e)}), 500

@market_data_bp.route('/indicators', methods=['GET'])
def get_indicators():
    """
    获取指定股票的多项技术指标（OBV, VMA, VR, MFI, PMA等），返回标准化结构。
    参数: ts_code, start_date, end_date, period, 可选: ma_windows, vma_windows
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        ts_code = request.args.get('ts_code')
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        ma_windows = request.args.get('ma_windows', '5,20,60')
        vma_windows = request.args.get('vma_windows', '5')
        logger.info(f"收到指标请求: ts_code={ts_code}, period={period}, start_date={start_date}, end_date={end_date}, ma_windows={ma_windows}, vma_windows={vma_windows}")
        if not all([ts_code, period, start_date, end_date]):
            logger.warning(f"参数缺失: ts_code={ts_code}, period={period}, start_date={start_date}, end_date={end_date}")
            return jsonify({'error': '缺少必要参数'}), 400
        # 用 datetime 对象严格校验日期
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            today_dt = datetime.now()
            if start_dt > today_dt or end_dt > today_dt:
                logger.warning(f"收到未来日期参数: start_date={start_date}, end_date={end_date}, today={today_dt.strftime('%Y%m%d')}")
                return jsonify({'error': '日期不能为未来'}), 400
        except Exception as ex:
            logger.warning(f'日期格式错误: start_date={start_date}, end_date={end_date}, ex={ex}')
            return jsonify({'error': '日期格式错误，应为YYYYMMDD'}), 400
        df = akshare_service.get_stock_historical_data(ts_code, period, start_date, end_date)
        if df is None or df.empty:
            logger.info(f"无行情数据: ts_code={ts_code}, period={period}, start_date={start_date}, end_date={end_date}")
            return jsonify({'error': '未获取到行情数据'}), 404
        # 字段标准化
        df = df.rename(columns={
            'trade_date': 'date', 'vol': 'volume', 'amount': 'amount'
        })
        df = df.sort_values('date')
        result = {
            'dates': df['date'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist(),
        }
        # OBV
        result['obv'] = TechnicalIndicators.calculate_obv(df).tolist()
        # VMA（支持多窗口）
        for w in [int(x) for x in vma_windows.split(',') if x.strip().isdigit()]:
            result[f'vma_{w}'] = TechnicalIndicators.calculate_vma(df, window=w).tolist()
        # VR
        result['vr'] = TechnicalIndicators.calculate_vr(df).tolist()
        # MFI
        result['mfi'] = TechnicalIndicators.calculate_mfi(df).tolist()
        # PMA（支持多窗口）
        for w in [int(x) for x in ma_windows.split(',') if x.strip().isdigit()]:
            result[f'pma_{w}'] = TechnicalIndicators.calculate_pma(df, window=w).tolist()
        # 递归将所有 NaN 替换为 None
        def replace_nan_with_none(obj):
            if isinstance(obj, list):
                return [replace_nan_with_none(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: replace_nan_with_none(v) for k, v in obj.items()}
            elif isinstance(obj, float) and (np.isnan(obj) or pd.isna(obj)):
                return None
            else:
                return obj
        result = replace_nan_with_none(result)
        return jsonify(result)
    except Exception as e:
        logger.error(f'获取技术指标API异常: {e}, ts_code={request.args.get("ts_code")}, period={request.args.get("period")}, start_date={request.args.get("start_date")}, end_date={request.args.get("end_date")}', exc_info=True)
        return jsonify({'error': str(e)}), 500 