import yfinance as yf
import json
from datetime import datetime

print("📊 更新 MA 訊號...")

# 獲取 NASDAQ 數據
ticker = yf.Ticker('^IXIC')
hist = ticker.history(period='1y')

# 計算 MA
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['MA200'] = hist['Close'].rolling(window=200).mean()

# 最新數據
latest = hist.iloc[-1]
price = latest['Close']
ma20 = latest['MA20']
ma200 = latest['MA200']

# 判斷訊號
signal = 'BULLISH' if (price > ma20 and ma20 > ma200) else 'BEARISH'
allocation = '65/20/15' if signal == 'BULLISH' else '50/10/40'

result = {
    'timestamp': datetime.now().isoformat(),
    'price': float(price),
    'ma20': float(ma20),
    'ma200': float(ma200),
    'signal': signal,
    'allocation': allocation
}

with open('data/signals.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"訊號: {signal}")
print(f"配置: {allocation}")
print("✅ 完成")
