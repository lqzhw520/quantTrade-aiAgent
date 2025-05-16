import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

# 保证可以导入服务模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services import akshare_service

class TestAkshareService(unittest.TestCase):
    @patch('akshare.stock_info_a_code_name')
    def test_get_stock_list_success(self, mock_stock_info):
        import pandas as pd
        mock_df = pd.DataFrame({
            'code': ['000001', '000002'],
            'name': ['平安银行', '万科A']
        })
        mock_stock_info.return_value = mock_df
        result = akshare_service.get_stock_list()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('ts_code', result[0])
        self.assertIn('name', result[0])

    @patch('akshare.stock_info_a_code_name')
    def test_get_stock_list_exception(self, mock_stock_info):
        mock_stock_info.side_effect = Exception('API error')
        with self.assertRaises(Exception):
            akshare_service.get_stock_list()

    @patch('akshare.stock_zh_a_hist')
    def test_get_stock_historical_data_daily(self, mock_hist):
        import pandas as pd
        mock_df = pd.DataFrame({
            '日期': ['20230101', '20230102'],
            '开盘': [10, 10.5],
            '收盘': [10.5, 11],
            '最高': [11, 12],
            '最低': [9, 10],
            '成交量': [1000, 1200],
            '成交额': [10000, 12000]
        })
        mock_hist.return_value = mock_df
        df = akshare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')
        self.assertIsNotNone(df)
        self.assertIn('trade_date', df.columns)
        self.assertIn('open', df.columns)
        self.assertIn('close', df.columns)
        self.assertIn('vol', df.columns)

    @patch('akshare.stock_zh_a_hist')
    def test_get_stock_historical_data_empty(self, mock_hist):
        import pandas as pd
        mock_df = pd.DataFrame()
        mock_hist.return_value = mock_df
        df = akshare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')
        self.assertIsNone(df)

    @patch('akshare.stock_zh_a_hist')
    def test_get_stock_historical_data_exception(self, mock_hist):
        mock_hist.side_effect = Exception('API error')
        with self.assertRaises(Exception):
            akshare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')

    def test_get_stock_historical_data_invalid_period(self):
        with self.assertRaises(ValueError):
            akshare_service.get_stock_historical_data('000001.SZ', 'invalid', '20230101', '20230131')

if __name__ == '__main__':
    unittest.main() 