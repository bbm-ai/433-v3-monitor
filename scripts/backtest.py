import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

print("🔄 執行回測...")

# 配置
INITIAL_CAPITAL = 20000000
PERIOD_YEARS = 3

# 獲取數據
ticker = yf.Ticker('^IXIC')
end = datetime.now()
start = end - timedelta(days=PERIOD_YEARS * 365)
hist = ticker.history(start=start, end=end)

# 計算 MA
hist['MA20'] = hist['Close'].rolling(window=20).mean()
hist['MA200'] = hist['Close'].rolling(window=200).mean()

# 回測
capital = INITIAL_CAPITAL
results = []

for i in range(200, len(hist)):
    price = hist['Close'].iloc[i]
    ma20 = hist['MA20'].iloc[i]
    ma200 = hist['MA200'].iloc[i]
    
    # 判斷訊號
    if price > ma20 and ma20 > ma200:
        # 多頭：65/20/15
        core_weight = 0.65
        lev_weight = 0.20
    else:
        # 空頭：50/10/40
        core_weight = 0.50
        lev_weight = 0.10
    
    # 計算報酬（簡化）
    price_change = (price - hist['Close'].iloc[i-1]) / hist['Close'].iloc[i-1]
    portfolio_return = (core_weight * price_change + 
                       lev_weight * price_change * 2)
    
    capital *= (1 + portfolio_return)
    
    results.append({
        'date': hist.index[i].strftime('%Y-%m-%d'),
        'capital': capital
    })

# 計算績效
final = results[-1]['capital']
total_return = (final - INITIAL_CAPITAL) / INITIAL_CAPITAL
annual_return = (1 + total_return) ** (1 / PERIOD_YEARS) - 1

print(f"年化報酬: {annual_return * 100:.2f}%")
print(f"{'✅ 達標' if annual_return * 100 >= 17 else '❌ 未達標'}")

# 保存
output = {
    'timestamp': datetime.now().isoformat(),
    'annual_return': annual_return * 100,
    'final_capital': final,
    'meets_target': annual_return * 100 >= 17
}

with open('data/backtest.json', 'w') as f:
    json.dump(output, f, indent=2)
