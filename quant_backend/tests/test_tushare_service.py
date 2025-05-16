import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

# 保证可以导入服务模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services import tushare_service

class TestTushareService(unittest.TestCase):
    @patch.dict(os.environ, {'TUSHARE_TOKEN': 'FAKE_TOKEN'})
    @patch('tushare.pro_api')
    def test_get_stock_list_success(self, mock_pro_api):
        # 模拟 tushare 返回 DataFrame
        mock_pro = MagicMock()
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [
            {'ts_code': '000001.SZ', 'name': '平安银行'},
            {'ts_code': '000002.SZ', 'name': '万科A'}
        ]
        mock_pro.stock_basic.return_value = mock_df
        mock_pro_api.return_value = mock_pro
        # 重新加载模块以应用 mock
        import importlib
        importlib.reload(tushare_service)
        result = tushare_service.get_stock_list()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('ts_code', result[0])
        self.assertIn('name', result[0])

    @patch.dict(os.environ, {}, clear=True)
    def test_get_stock_list_no_token(self):
        import importlib
        importlib.reload(tushare_service)
        result = tushare_service.get_stock_list()
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TUSHARE_TOKEN': 'FAKE_TOKEN'})
    @patch('tushare.pro_api')
    def test_get_stock_list_exception(self, mock_pro_api):
        mock_pro = MagicMock()
        mock_pro.stock_basic.side_effect = Exception('API error')
        mock_pro_api.return_value = mock_pro
        import importlib
        importlib.reload(tushare_service)
        result = tushare_service.get_stock_list()
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TUSHARE_TOKEN': 'FAKE_TOKEN'})
    @patch('tushare.pro_api')
    def test_get_stock_historical_data_daily(self, mock_pro_api):
        mock_pro = MagicMock()
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.sort_values.return_value = mock_df
        mock_pro.daily.return_value = mock_df
        mock_pro.weekly.return_value = mock_df
        mock_pro.monthly.return_value = mock_df
        mock_pro_api.return_value = mock_pro
        import importlib
        importlib.reload(tushare_service)
        # 日线
        df = tushare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')
        self.assertIsNotNone(df)
        # 周线
        df2 = tushare_service.get_stock_historical_data('000001.SZ', 'weekly', '20230101', '20230131')
        self.assertIsNotNone(df2)
        # 月线
        df3 = tushare_service.get_stock_historical_data('000001.SZ', 'monthly', '20230101', '20230131')
        self.assertIsNotNone(df3)

    @patch.dict(os.environ, {'TUSHARE_TOKEN': 'FAKE_TOKEN'})
    @patch('tushare.pro_api')
    def test_get_stock_historical_data_empty(self, mock_pro_api):
        mock_pro = MagicMock()
        mock_df = MagicMock()
        mock_df.empty = True
        mock_pro.daily.return_value = mock_df
        mock_pro_api.return_value = mock_pro
        import importlib
        importlib.reload(tushare_service)
        df = tushare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')
        self.assertIsNone(df)

    @patch.dict(os.environ, {'TUSHARE_TOKEN': 'FAKE_TOKEN'})
    @patch('tushare.pro_api')
    def test_get_stock_historical_data_exception(self, mock_pro_api):
        mock_pro = MagicMock()
        mock_pro.daily.side_effect = Exception('API error')
        mock_pro_api.return_value = mock_pro
        import importlib
        importlib.reload(tushare_service)
        df = tushare_service.get_stock_historical_data('000001.SZ', 'daily', '20230101', '20230131')
        self.assertIsNone(df)

    def test_get_stock_historical_data_invalid_period(self):
        import importlib
        importlib.reload(tushare_service)
        df = tushare_service.get_stock_historical_data('000001.SZ', 'invalid', '20230101', '20230131')
        self.assertIsNone(df)

if __name__ == '__main__':
    unittest.main() 