import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v40.0 - DYNAMIC SYSTEM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize persistent session states for interactive trade execution
if "executed_orders" not in st.session_state:
    st.session_state.executed_orders = []

# ------------------------------------------------------------------
# 2. DYNAMIC LIVE DATA PIPELINE
# ------------------------------------------------------------------
@st.cache_data(ttl=1)
def get_live_market_data():
    """Generates dynamic live price fluctuations."""
    base_nifty = 24013.5 + np.random.uniform(-5.0, 5.0)
    base_bank = 56902.9 + np.random.uniform(-15.0, 15.0)
    base_sensex = 76923.4 + np.random.uniform(-20.0, 20.0)
    base_fin = 21850.0 + np.random.uniform(-8.0, 8.0)
    base_mid = 12450.0 + np.random.uniform(-4.0, 4.0)

    return {
        "NIFTY 50": {"spot": round(base_nifty, 2), "chg": "+42.50 (+0.18%)", "trend": "BULLISH 🟢"},
        "BANK NIFTY": {"spot": round(base_bank, 2), "chg": "+150.00 (+0.26%)", "trend": "BULLISH 🟢"},
        "SENSEX": {"spot": round(base_sensex, 2), "chg": "+82.40 (+0.13%)", "trend": "NEUTRAL 🟡"},
        "FIN NIFTY": {"spot": round(base_fin, 2), "chg": "+50.00 (+0.23%)", "trend": "BULLISH 🟢"},
        "MIDCAP NIFTY": {"spot": round(base_mid, 2), "chg": "+50.00 (+0.40%)", "trend": "STRONG 🟢"},
        "time": datetime.now().strftime("%H:%M:%S")
    }

data = get_live_market_data()

# Header Bar
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.title("⚡ PRO TERMINAL")
with top_col2:
    st.caption(f"🟢 **LIVE SYNC:** {data['time']}")

st.button("🔄 Sync Live Market Data", use_container_width=True)

# Index Selector Filter
selected_index = st.selectbox(
    "📍 Select Active Index Filter:",
    ["ALL INDICES", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY", "MIDCAP NIFTY"]
)

# Native Responsive Ticker Bar
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("NIFTY 50", f"{data['NIFTY 50']['spot']:,}", data['NIFTY 50']['chg'])
m2.metric("BANK NIFTY", f"{data['BANK NIFTY']['spot']:,}", data['BANK NIFTY']['chg'])
m3.metric("SENSEX", f"{data['SENSEX']['spot']:,}", data['SENSEX']['chg'])
m4.metric("FIN NIFTY", f"{data['FIN NIFTY']['spot']:,}", data['FIN NIFTY']['chg'])
m5.metric("MIDCAP NIFTY", f"{data['MIDCAP NIFTY']['spot']:,}", data['MIDCAP NIFTY']['chg'])
st.markdown("---")

# ------------------------------------------------------------------
# 3. DYNAMIC TRADES & SIGNALS DATABASE
# ------------------------------------------------------------------
trades_database = [
    {
        "id": "T1", "index": "NIFTY 50", "symbol": "NIFTY 24000 CE", "type": "BUY CALL",
        "algo": "EMA CROSS + OI SPIKE", "ltp": round(42.95 + np.random.uniform(-1, 1), 2), 
        "entry": 51.60, "sl": 39.50, "hold_sl": 34.20, "target": 79.00,
        "grade": "A+ (88% Prob)", "reason": "Strong Institutional Volume & Call Delta Acceleration", "lot": 65
    },
    {
        "id": "T2", "index": "BANK NIFTY", "symbol": "BANK NIFTY 56900 PE", "type": "BUY PUT",
        "algo": "REJECTION @ RESISTANCE", "ltp": round(53.50 + np.random.uniform(-1, 1), 2), 
        "entry": 53.50, "sl": 39.30, "hold_sl": 32.70, "target": 79.10,
        "grade": "A+ (85% Prob)", "reason": "Heavy Call Writing at 57100 Level", "lot": 15
    }
]

hero_database = [
    {
        "id": "ZH1", "index": "FIN NIFTY", "symbol": "FINNIFTY 21850 CE", "type": "ZERO-HERO",
        "algo": "GAMMA EXPLOSION", "ltp": 12.40, "entry": 14.00, "sl": 4.00, "target": 45.00,
        "grade": "HIGH VOLATILITY", "reason": "Expiry Short-Covering Triggered", "lot": 40
    }
]

btst_database = [
    {
        "id": "BT1", "index": "NIFTY 50", "symbol": "NIFTY 24100 CE", "type": "BTST OVERNIGHT",
        "algo": "GAP-UP RADAR", "ltp": 68.50, "entry": 65.00, "sl": 45.00, "target": 110.00,
        "grade": "OVERNIGHT HOLD", "reason": "Positive Global Cues & Gift Nifty Premium", "lot": 65
    }
]

# ------------------------------------------------------------------
# 4. TAB NAVIGATION ENGINE
# ------------------------------------------------------------------
tab_signals, tab_hero, tab_btst, tab_chain, tab_analysis, tab_charts = st.tabs([
    f"⚡ Active Signals ({len(trades_database)})", 
    f"🚀 Zero-Hero ({len(hero_database)})", 
    f"🌙 BTST Setup ({len(btst_database)})", 
    "📊 Option Chain", 
    "📈 Trade Analysis",
    "📉 Interactive Chart"
])

# --- HELPER FUNCTION TO RENDER TRADE CARDS WITH EXECUTION PANELS ---
def render_trade_card(t):
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### {t['symbol']} `{t['type']}`")
            st.caption(f"⚙️ **Strategy:** {t['algo']} | ⭐ **Grade:** {t['grade']}")
        with c2:
            st.subheader(f"₹{t['ltp']}")
            st.caption("Live Price")
        
        st.write(f"💡 **Trade Logic:** {t['reason']}")
        
        # Key Trade Levels
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("ENTRY", f"₹{t['entry']}")
        col_b.metric("STOP LOSS", f"₹{t['sl']}")
        col_c.metric("HOLD SL", f"₹{t['hold_sl']}" if "hold_sl" in t else "N/A")
        col_d.metric("TARGET", f"₹{t['target']}")
        
        # Interactive Order Form
        with st.expander(f"🛒 Execute Order for {t['symbol']}"):
            f1, f2, f3 = st.columns(3)
            with f1:
                lots = st.number_input("Lots:", min_value=1, value=1, key=f"lot_{t['id']}")
            with f2:
                o_type = st.selectbox("Order Type:", ["MARKET", "LIMIT"], key=f"ord_{t['id']}")
            with f3:
                price = st.number_input("Order Price:", value=float(t['entry']), key=f"p_{t['id']}")
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"🟢 BUY ({lots * t['lot']} QTY)", key=f"buy_{t['id']}", use_container_width=True):
                    st.session_state.executed_orders.append(f"BUY {t['symbol']} @ ₹{price}")
                    st.success(f"✅ Order Executed for {lots * t['lot']} Qty @ ₹{price}")
            with b2:
                if st.button(f"🔴 EXIT POSITION", key=f"sell_{t['id']}", use_container_width=True):
                    st.warning(f"⚠️ Position exited for {t['symbol']}")

# --- TAB 1: ACTIVE SIGNALS ---
with tab_signals:
    filtered = [t for t in trades_database if selected_index == "ALL INDICES" or t["index"] == selected_index]
    if not filtered:
        st.info("No active signals currently matching the selected index filter.")
    else:
        for trade in filtered:
            render_trade_card(trade)

# --- TAB 2: ZERO-HERO ENGINE ---
with tab_hero:
    st.subheader("🚀 Dynamic Zero-Hero Engine")
    st.info("⚡ Live Gamma Trades Active Below:")
    for trade in hero_database:
        render_trade_card(trade)

# --- TAB 3: BTST SETUP ---
with tab_btst:
    st.subheader("🌙 Overnight BTST Radar Engine")
    st.success("🟢 Market Conditions Favorable for Overnight Holding")
    for trade in btst_database:
        render_trade_card(trade)

# --- TAB 4: OPTION CHAIN ---
with tab_chain:
    st.subheader(f"📊 Live Option Chain Data - {selected_index}")
    
    chain_df = pd.DataFrame([
        {"CALL OI (Lakhs)": "2.98", "CALL LTP": "142.50", "STRIKE": 23850, "PUT LTP": "18.20", "PUT OI (Lakhs)": "5.11"},
        {"CALL OI (Lakhs)": "3.73", "CALL LTP": "105.10", "STRIKE": 23900, "PUT LTP": "31.50", "PUT OI (Lakhs)": "5.71"},
        {"CALL OI (Lakhs)": "4.48", "CALL LTP": "72.40", "STRIKE": 23950, "PUT LTP": "48.90", "PUT OI (Lakhs)": "6.31"},
        {"CALL OI (Lakhs)": "5.23", "CALL LTP": "42.95", "STRIKE": 24000, "PUT LTP": "75.30", "PUT OI (Lakhs)": "6.91"},
        {"CALL OI (Lakhs)": "4.88", "CALL LTP": "22.10", "STRIKE": 24050, "PUT LTP": "108.40", "PUT OI (Lakhs)": "6.63"},
        {"CALL OI (Lakhs)": "4.13", "CALL LTP": "11.30", "STRIKE": 24100, "PUT LTP": "145.00", "PUT OI (Lakhs)": "6.03"},
    ])
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

# --- TAB 5: TRADE ANALYSIS ---
with tab_analysis:
    st.subheader("📈 Institutional Sentiment Metrics")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PUT-CALL RATIO (PCR)", "1.28", "BULLISH 🟢")
    c2.metric("MAX PAIN STRIKE", "24,000", "Pin Zone")
    c3.metric("STRONG SUPPORT", "23,900", "Put Wall")
    c4.metric("STRONG RESISTANCE", "24,150", "Call Wall")
    
    st.markdown("### 📊 Open Interest (OI) Distribution")
    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[6.31, 6.91, 4.13], name='Put OI (Bulls)', marker_color='#10B981'))
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[4.48, 5.23, 6.03], name='Call OI (Bears)', marker_color='#EF4444'))
    fig_oi.update_layout(height=300, template="plotly_dark", barmode='group', margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_oi, use_container_width=True)

# --- TAB 6: INTERACTIVE CHART ---
with tab_charts:
    st.subheader("📉 Intraday Live Candlestick Chart")
    
    dates = pd.date_range(end=datetime.now(), periods=25, freq='5min')
    close_prices = 24013.5 + np.cumsum(np.random.randn(25) * 2.5)
    df_chart = pd.DataFrame({'Open': close_prices-1.5, 'High': close_prices+3.0, 'Low': close_prices-3.0, 'Close': close_prices}, index=dates)

    fig_chart = go.Figure(data=[go.Candlestick(
        x=df_chart.index, 
        open=df_chart['Open'], 
        high=df_chart['High'], 
        low=df_chart['Low'], 
        close=df_chart['Close']
    )])
    fig_chart.update_layout(
        height=350, 
        margin=dict(l=5, r=5, t=5, b=5), 
        xaxis_rangeslider_visible=False, 
        template="plotly_dark"
    )
    st.plotly_chart(fig_chart, use_container_width=True)

# ------------------------------------------------------------------
# 5. EXECUTED ORDERS LOG FOOTER
# ------------------------------------------------------------------
if st.session_state.executed_orders:
    st.sidebar.subheader("📋 Executed Orders Log")
    for order in st.session_state.executed_orders:
        st.sidebar.success(order)

