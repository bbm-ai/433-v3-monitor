import streamlit as st
import requests
import pandas as pd

# ==========================
# 🔧 設定區
# ==========================

# 若在 Streamlit Cloud 設定了 Secrets，這裡會優先讀取
try:
    GAS_API_URL = st.secrets["GAS_API_URL"]
except KeyError:
    # 本地測試用 (請修改為您的實際網址)
    GAS_API_URL = "https://script.google.com/macros/s/Your_ID/exec"

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
    
    # 安全讀取 data portfolio
    portfolio = data.get('portfolio', {})
    total_val = portfolio.get('totalValue', 0)
    
    with col1:
        st.metric(
            label="總資產", 
            value=f"NT$ {total_val:,}", 
            delta=f"Beta: {portfolio.get('beta', 0)}"
        )

    # 安全讀取 data v3
    v3 = data.get('v3', {})
    dd = v3.get('drawdown', 0)
    stage = v3.get('stage', 0)
    
    with col2:
        # 根據跌幅調整 delta 顏色
        delta_color = "inverse" if dd > 20 else "normal"
        st.metric(
            label="QLD 回撤", 
            value=f"{dd:.2f}%", 
            delta=f"第 {stage} 階段",
            delta_color=delta_color
        )

    # 安全讀取 data safety
    safety = data.get('safety', {})
    mrate = safety.get('maintenanceRate', 999)
    
    with col3:
        # 維持率低於 220% 變紅
        color = "inverse" if mrate < 220 else "normal"
        st.metric(
            label="維持率",
            value=f"{int(mrate)}%",
            help="資產覆蓋借款的比例，低於 220% 需注意",
            delta_color=color
        )
        
    # 安全讀取 data mode
    mode = data.get('mode', {})
    active_mode = mode.get('active', 'N/A')
        
    with col4:
        st.metric(label="目前模式", value=active_mode.upper())

    st.markdown("---")

    # ==========================================
    # 2. 實際配置 vs 建議配置
    # ==========================================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("💼 資產分配 (實際)")
        
        # 組裝表格資料
        suggested = v3.get('suggestedWeights', {})
        actual_weights = portfolio.get('weights', {})
        prices = data.get('prices', {})
        shares = data.get('shares', {})
        
        # 計算市值顯示
        val_c = shares.get('core', 0) * prices.get('core', 0)
        val_l = shares.get('leverage', 0) * prices.get('leverage', 0)
        val_s = shares.get('cash', 0) * prices.get('cash', 0)

        df_data = {
            "類別": ["Core", "Leverage", "Cash"],
            "建議權重 (%)": [suggested.get('core', 0), suggested.get('leverage', 0), suggested.get('cash', 0)],
            "實際權重 (%)": [actual_weights.get('core', 0), actual_weights.get('leverage', 0), actual_weights.get('cash', 0)],
            "持股市值": [
                f"NT$ {val_c:,.0f}",
                f"NT$ {val_l:,.0f}",
                f"NT$ {val_s:,.0f}"
            ]
        }
        
        st.table(pd.DataFrame(df_data))

    with col_right:
        st.subheader("🎯 7年翻倍目標追蹤")
        
        # 安全讀取 goal，包含 daysPassed
        goal = data.get('goal', {})
        progress = goal.get('progressPct', 0)
        ideal = goal.get('idealValue', 0)
        target = goal.get('targetValue', 0)
        
        # 🔧 關鍵修正：使用 .get() 避免 KeyError
        days_passed = goal.get('daysPassed', 0)
        
        # 進度條
        st.progress(progress / 100)
        st.write(f"距離起點已過 **{days_passed}** 天 (總進度 {progress:.1f}%)")
        
        # 判斷狀態 logic
        if total_val >= ideal:
            st.success(f"✅ **狀況優良** (目前資產高於理想進度曲線)")
            st.write(f"理想值: NT$ {ideal:,} | 目前值: NT$ {total_val:,}")
        else:
            st.warning(f"⚠️ **需加強** (目前資產低於理想進度曲線)")
            shortfall = ideal - total_val
            st.write(f"理想值: NT$ {ideal:,} | 差距: NT$ {shortfall:,}")

    # ==========================================
    # 3. 警報與通知
    # ==========================================
    alerts = data.get('alerts', [])
    if alerts:
        st.subheader("⚠️ 注意事項")
        for alert in alerts:
            level = alert.get('level', 'info')
            atype = alert.get('type', 'Unknown')
            msg = alert.get('message', '')
            
            if level == 'critical':
                st.error(f"🔴 **{atype}**: {msg}")
            elif level == 'warning':
                st.warning(f"🟡 **{atype}**: {msg}")
            else:
                st.info(f"ℹ️ **{atype}**: {msg}")
    else:
        st.success("🟢 系統運作正常，無需調整警報。")

if __name__ == "__main__":
    main()
