"""數據獲取模組"""
import yfinance as yf
from datetime import datetime
import json

class MarketDataFetcher:
    TICKERS = {
        'core': '00662.TW',
        'leverage': '00670L.TW',
        'cash': '00865B.TW'
    }
    
    @classmethod
    def fetch_current_prices(cls):
        """獲取當前價格"""
        prices = {}
        for key, ticker in cls.TICKERS.items():
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                prices[key] = {
                    'price': info.get('regularMarketPrice') or info.get('currentPrice'),
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                prices[key] = None
        return prices
    
    @classmethod
    def fetch_historical_high(cls, ticker, period='max'):
        """獲取歷史最高價"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist['High'].max()
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None

if __name__ == '__main__':
    # 測試
    fetcher = MarketDataFetcher()
    prices = fetcher.fetch_current_prices()
    print(json.dumps(prices, indent=2))
