import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# ==========================
# 🔧 設定區
# ==========================
# 請將 GAS_API_URL 替換為您的 API 網址
# 如果在 Streamlit Cloud 設定了 Secrets，這裡 st.secrets 會優先讀取
try:
    GAS_API_URL = st.secrets["GAS_API_URL"]
except KeyError:
    # 本地測試用
    GAS_API_URL = "https://script.google.com/macros/s/AKfycbx_CHANGE_YOUR_ID_HERE/exec"

# ========================================
# 🎨 儀表板主程式
# ========================================
def main():
    st.set_page_config(
        page_title="433-v3 監控儀表板",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 433-v3 策略監控儀表板")

    # 獲取數據
    try:
        response = requests.get(GAS_API_URL)
        response.raise_for_status() # 檢查 HTTP 錯誤
        data = response.json()
    except Exception as e:
        st.error(f"無法獲取數據: {e}")
        return

    # ==========================================
    # 1. 關鍵指標
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 修正這裡：從 portfolio.totalValue 讀取
        total_val = data['portfolio']['totalValue']
        st.metric(
            label="總資產", 
            value=f"NT$ {total_val:,}", 
            delta=f"Beta: {data['portfolio']['beta']}"
        )

    with col2:
        # 修正這裡：從 v3.drawdown 讀取
        dd = data['v3']['drawdown']
        stage = data['v3']['stage']
        st.metric(
            label="QLD 回撤", 
            value=f"{dd:.2f}%", 
            delta=f"第 {stage} 階段",
            delta_color="inverse" if dd > 0 else "normal"
        )

    with col3:
        # 修正這裡：從 safety.maintenanceRate 讀取
        mrate = data['safety']['maintenanceRate']
        color = "normal" if mrate >= 220 else "inverse"
        st.metric(
            label="維持率",
            value=f"{int(mrate)}%",
            help="資產覆蓋借款的比例，低於 220% 需注意",
            delta_color=color
        )
        
    with col4:
        # 新增欄位：顯示目前模式
        mode = data['mode']['active']
        st.metric(label="目前模式", value=mode.upper())

    st.markdown("---")

    # ==========================================
    # 2. 實際配置 vs 建議配置 (表格)
    # ==========================================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("💼 資產分配 (實際)")
        # 資料準備
        actual_df = pd.DataFrame({
            "類別": ["Core", "Leverage", "Cash"],
            "建議權重 (%)": [
                data['v3']['suggestedWeights']['core'],
                data['v3']['suggestedWeights']['leverage'],
                data['v3']['suggestedWeights']['cash']
            ],
            "實際權重 (%)": [
                data['portfolio']['weights']['core'],
                data['portfolio']['weights']['leverage'],
                data['portfolio']['weights']['cash']
            ],
            "持股市值": [
                f"NT$ {data['shares']['core'] * data['prices']['core']:,.0f}",
                f"NT$ {data['shares']['leverage'] * data['prices']['leverage']:,.0f}",
                f"NT$ {data['shares']['cash'] * data['prices']['cash']:,.0f}"
            ]
        })
        st.table(actual_df)

    with col_right:
        st.subheader("🎯 7年翻倍目標追蹤")
        
        goal = data['goal']
        progress = goal['progressPct']
        ideal = goal['idealValue']
        target = goal['targetValue']
        total = data['portfolio']['totalValue']
        
        # 進度條
        st.progress(progress / 100)
        st.write(f"距離起點已過 **{goal['daysPassed']}** 天 (總進度 {progress:.1f}%)")
        
        # 判斷狀態
        if total >= ideal:
            st.success(f"✅ **狀況優良** (目前資產高於理想進度曲線)")
            st.write(f"理想值: NT$ {ideal:,} | 目前值: NT$ {total:,}")
        else:
            st.warning(f"⚠️ **需加強** (目前資產低於理想進度曲線)")
            shortfall = ideal - total
            st.write(f"理想值: NT$ {ideal:,} | 差距: NT$ {shortfall:,}")

    # ==========================================
    # 3. 警報與通知
    # ==========================================
    if data['alerts']:
        st.subheader("⚠️ 注意事項")
        for alert in data['alerts']:
            if alert['level'] == 'critical':
                st.error(f"🔴 **{alert['type']}**: {alert['message']}")
            elif alert['level'] == 'warning':
                st.warning(f"🟡 **{alert['type']}**: {alert['message']}")
            else:
                st.info(f"ℹ️ **{alert['type']}**: {alert['message']}")
    else:
        st.success("🟢 系統運作正常，無需調整警報。")

if __name__ == "__main__":
    main()
