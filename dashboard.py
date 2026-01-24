import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ============================
# 設定區
# ============================
# 讀取 Secrets，如果本地執行則讀取不到，需處理異常
try:
    GAS_API_URL = st.secrets["GAS_API_URL"]
except KeyError:
    GAS_API_URL = "本地測試用的URL" # 您本地的 GAS API
st.set_page_config(page_title="BBM 智慧監控儀表板", layout="wide")

# ============================
# 資料讀取功能
# ============================
@st.cache_data(ttl=300) # 快取 5 分鐘
def load_data():
    try:
        response = requests.get(GAS_API_URL)
        data = response.json()
        return data
    except Exception as e:
        st.error(f"無法連線 GAS: {e}")
        return None

# ============================
# 網頁開始
# ============================
st.title("📊 433-v3 投資監控與模擬系統")
data = load_data()

if data:
    # --- Layout: 關鍵指標 ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("目前模式", data['mode']['active'], delta="(433/532/442)")
    with col2:
        total_val = data['current']['total']
        st.metric("總資產", f"NT$ {total_val:,}", 
                  delta=f"{data['current']['drawdown_pct']:.2f}% QLD")
    with col3:
        st.metric("組合 Beta", f"{data['current']['beta']:.2f}", 
                  delta="目標範圍 1.3 - 1.6")
    with col4:
        progress = data['goal']['progress_pct']
        st.metric("7年目標進度", f"{progress:.1f}%", 
                  delta=f"理想值: NT$ {data['goal']['idealValue']:,}")

    st.divider()

    # --- Layout: 圖表區 ---
    chart_col1, chart_col2 = st.columns(2)

    # 1. 7 年成長曲線
    with chart_col1:
        st.subheader("📈 成長曲線 vs 目標")
        progress_val = data['goal']['progress_pct']
        current_val = data['goal']['currentValue']
        ideal_val = data['goal']['idealValue']
        init_val = data['goal']['initValue']
        
        # 模擬成長曲線數據 (視覺化用)
        days = [0, data['goal']['daysPassed'], data['goal']['totalDays']]
        curve_start = [init_val, ideal_val, data['goal']['targetValue']]
        curve_linear = [init_val, init_val + (data['goal']['targetValue']-init_val)*(progress_val/100), data['goal']['targetValue']]
        curve_actual = [init_val, current_val, data['goal']['targetValue']] # 假定未來達成(視覺效果)

        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(x=days, y=curve_start, mode='lines+markers', name='複利曲線 (10.4%)', line=dict(color='gold', width=3)))
        fig_growth.add_trace(go.Scatter(x=days, y=curve_actual, mode='lines+markers', name='實際績效', line=dict(color='blue', width=3)))
        
        fig_growth.update_layout(height=300, yaxis_title="資產價值 (TWD)")
        st.plotly_chart(fig_growth, use_container_width=True)

    # 2. 風險溫度計
    with chart_col2:
        st.subheader("🌡️ v3 風險溫度計")
        dd = abs(data['current']['drawdown_pct'])
        stage = data['mode']['v3_stage']
        
        # 使用 Gauge Chart
        fig_temp = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = dd,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"當前回撤 (階段 {stage})"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': '#32CD32'}, # Safe
                    {'range': [20, 35], 'color': '#FFD700'}, # Warning
                    {'range': [35, 50], 'color': '#FF4500'}, # Danger
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 40}
            }
        ))
        fig_temp.update_layout(height=300)
        st.plotly_chart(fig_temp, use_container_width=True)

    st.divider()

    # --- Layout: 互動與建議 ---
    info_col1, info_col2 = st.columns([1, 1])

    with info_col1:
        st.subheader("⚖️ 配置建議與對比")
        df_weights = pd.DataFrame({
            'Asset': ['Core', 'Leverage', 'Cash'],
            '目前': [data['current']['weights']['core']*100, data['current']['weights']['leverage']*100, data['current']['weights']['cash']*100],
            '目標': [data['mode']['target_weights']['core']*100, data['mode']['target_weights']['leverage']*100, data['mode']['target_weights']['cash']*100]
        })
        
        fig_bar = px.bar(df_weights, x="Asset", y=["目前", "目標"], barmode="group", title="權重差距分析", color_discrete_map={"目前": "lightblue", "目標": "navy"})
        st.plotly_chart(fig_bar, use_container_width=True)

    with info_col2:
        st.subheader("🔮 Beta 模擬計算器")
        st.info("拖曳滑桿模擬不同權重下的 Portfolio Beta")
        
        col_a, col_b = st.columns(2)
        with col_a:
            s_core = st.slider("Core 權重 (%)", 0, 100, int(data['current']['weights']['core']*100))
        with col_b:
            s_lev = st.slider("Leverage 權重 (%)", 0, 100, int(data['current']['weights']['leverage']*100))
        
        calc_beta = (s_core * 1.0 + s_lev * 2.0) / 100
        
        st.metric("預估 Beta", f"{calc_beta:.3f}")
        if calc_beta > 1.8:
            st.error("⚠️ 風險過高！")
        elif calc_beta > 1.4:
            st.warning("⚠️ 風險偏高")
        else:
            st.success("✅ 風險可控")

else:
    st.warning("正在等待數據載入...")

