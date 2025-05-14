import yfinance as yf
import os
import requests
from datetime import datetime, timedelta

def test_yahoo_finance_connection():
    # 测试直接访问 Yahoo Finance API
    url = "https://query1.finance.yahoo.com/v7/finance/download/TSLA"
    params = {
        "period1": int((datetime.now() - timedelta(days=30)).timestamp()),
        "period2": int(datetime.now().timestamp()),
        "interval": "1d",
        "events": "history"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Direct API Response Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.text[:200]}...")  # 只打印前200个字符
    except Exception as e:
        print(f"Direct API Error: {str(e)}")

def test_yfinance_download():
    try:
        # 使用 yfinance 下载数据
        ticker = yf.Ticker("TSLA")
        hist = ticker.history(period="1mo")
        print("\nYFinance Download Result:")
        print(hist.head())
    except Exception as e:
        print(f"YFinance Error: {str(e)}")

if __name__ == "__main__":
    print("Testing Yahoo Finance Connection...")
    test_yahoo_finance_connection()
    print("\nTesting YFinance Download...")
    test_yfinance_download() 