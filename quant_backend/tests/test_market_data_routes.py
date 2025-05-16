import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from quant_backend.api.market_data_routes import market_data_bp

class TestMarketDataRoutes(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(market_data_bp)
        self.client = app.test_client()

    @patch('quant_backend.services.akshare_service.get_stock_list')
    def test_stock_list_success(self, mock_get_stock_list):
        mock_get_stock_list.return_value = [
            {'ts_code': '000001.SZ', 'name': '平安银行'},
            {'ts_code': '000002.SZ', 'name': '万科A'}
        ]
        resp = self.client.get('/api/market_data/stock_list')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        self.assertIn('ts_code', data['data'][0])
        self.assertIn('name', data['data'][0])

    @patch('quant_backend.services.akshare_service.get_stock_list')
    def test_stock_list_fail(self, mock_get_stock_list):
        mock_get_stock_list.return_value = None
        resp = self.client.get('/api/market_data/stock_list')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertIn('error', data)

    @patch('quant_backend.services.akshare_service.get_stock_list')
    def test_stock_list_exception(self, mock_get_stock_list):
        mock_get_stock_list.side_effect = Exception('mock error')
        resp = self.client.get('/api/market_data/stock_list')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertIn('error', data)
        self.assertIn('mock error', data['error'])

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_historical_data_success(self, mock_get_hist):
        mock_df = pd.DataFrame({
            'trade_date': ['20230101', '20230102'],
            'open': [10, 10.5],
            'high': [11, 12],
            'low': [9, 10],
            'close': [10.5, 11],
            'vol': [1000, 1200],
            'amount': [10000, 12000]
        })
        mock_get_hist.return_value = mock_df
        params = '?ts_code=000001.SZ&period=daily&start_date=20230101&end_date=20230131'
        resp = self.client.get(f'/api/market_data/historical_data{params}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        self.assertIn('trade_date', data['data'][0])
        self.assertIn('open', data['data'][0])

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_historical_data_no_data(self, mock_get_hist):
        mock_get_hist.return_value = None
        params = '?ts_code=000001.SZ&period=daily&start_date=20230101&end_date=20230131'
        resp = self.client.get(f'/api/market_data/historical_data{params}')
        self.assertEqual(resp.status_code, 404)
        data = resp.get_json()
        self.assertIn('error', data)

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_historical_data_exception(self, mock_get_hist):
        mock_get_hist.side_effect = Exception('mock error')
        params = '?ts_code=000001.SZ&period=daily&start_date=20230101&end_date=20230131'
        resp = self.client.get(f'/api/market_data/historical_data{params}')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertIn('error', data)
        self.assertIn('mock error', data['error'])

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_indicators_success(self, mock_get_hist):
        df = pd.DataFrame({
            'trade_date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'open': [10, 11, 12, 13, 14],
            'high': [11, 12, 13, 14, 15],
            'low': [9, 10, 11, 12, 13],
            'close': [10, 11, 12, 13, 14],
            'vol': [1000, 1100, 1200, 1300, 1400],
            'amount': [10000, 11000, 12000, 13000, 14000]
        })
        mock_get_hist.return_value = df
        params = '?ts_code=000001.SZ&period=daily&start_date=20240101&end_date=20240105&ma_windows=5,20&vma_windows=5'
        resp = self.client.get(f'/api/market_data/indicators{params}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('dates', data)
        self.assertIn('close', data)
        self.assertIn('volume', data)
        self.assertIn('obv', data)
        self.assertIn('vma_5', data)
        self.assertIn('vr', data)
        self.assertIn('mfi', data)
        self.assertIn('pma_5', data)
        self.assertIn('pma_20', data)
        self.assertEqual(len(data['dates']), 5)
        self.assertEqual(len(data['obv']), 5)
        self.assertEqual(len(data['vma_5']), 5)
        self.assertEqual(len(data['vr']), 5)
        self.assertEqual(len(data['mfi']), 5)
        self.assertEqual(len(data['pma_5']), 5)
        self.assertEqual(len(data['pma_20']), 5)

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_indicators_no_data(self, mock_get_hist):
        mock_get_hist.return_value = None
        params = '?ts_code=000001.SZ&period=daily&start_date=20240101&end_date=20240105'
        resp = self.client.get(f'/api/market_data/indicators{params}')
        self.assertEqual(resp.status_code, 404)
        data = resp.get_json()
        self.assertIn('error', data)

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_indicators_exception(self, mock_get_hist):
        mock_get_hist.side_effect = Exception('mock error')
        params = '?ts_code=000001.SZ&period=daily&start_date=20240101&end_date=20240105'
        resp = self.client.get(f'/api/market_data/indicators{params}')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertIn('error', data)
        self.assertIn('mock error', data['error'])

    @patch('quant_backend.services.akshare_service.get_stock_historical_data')
    def test_indicators_future_date(self, mock_get_hist):
        # mock 不应被调用，但即使被调用也返回None
        mock_get_hist.return_value = None
        params = '?ts_code=000001.SZ&period=daily&start_date=29990101&end_date=29990105'
        resp = self.client.get(f'/api/market_data/indicators{params}')
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn('error', data)
        self.assertIn('未来', data['error'])

if __name__ == '__main__':
    unittest.main() 