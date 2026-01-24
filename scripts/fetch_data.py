import yfinance as yf
import json
import sys

TICKERS = {'core': '00662.TW', 'leverage': '00670L.TW', 'cash': '00865B.TW'}

data = {}
for key, ticker in TICKERS.items():
    stock = yf.Ticker(ticker)
    data[key] = {'price': stock.info.get('regularMarketPrice')}

print(json.dumps(data))
