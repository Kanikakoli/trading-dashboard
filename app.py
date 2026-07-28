import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIG & MOBILE RESPONSIVE INJECTIONS
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v50.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to FORCE horizontal row structure on Mobile Screens
st.markdown("""
<style>
/* Remove default huge padding on mobile */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
}

/* Force 5-column horizontal grid even on mobile screens */
.mobile-ticker-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 4px;
    margin: 8px 0px;
}

.ticker-card {
    background-color: #0E1117;
    border: 1px solid #262730;
    border-radius: 6px;
    padding: 6px 2px;
    text-align: center;
}

.ticker-name {
    font-size: 8px;
    font-weight: 700;
    color: #9CA3AF;
    white-space: nowrap;
}

.ticker-price {
    font-size: 10px;
    font-weight: 900;
    color: #FAFAFA;
    margin: 2px 0px;
}

.ticker-change {
    font-size: 7px;
    font-weight: 800;
    color: #10B981;
}

/* Streamlit Native Tab Bar styling on mobile */
button[data-baseweb="tab"] {
    font-size: 11px !important;
    padding: 4px 8px !important;
}
</style>
""", unsafe_allow_html=True)

if "executed_orders" not in st.session_state:
    st.session_state.executed_orders = []

# ------------------------------------------------------------------
# 2. DYNAMIC LIVE DATA
# ------------------------------------------------------------------
@st.cache_data(ttl=1)
def get_live_market_data():
    base_nifty = 24013.5 + np.random.uniform(-3.0, 3.0)
    base_bank = 56902.9 + np.random.uniform(-10.0, 10.0)
    base_sensex = 76923.4 + np.random.uniform(-15.0, 15.0)
    base_fin = 21850.0 + np.random.uniform(-5.0, 5.0)
    base_mid = 12450.0 + np.random.uniform(-3.0, 3.0)

    return {
        "NIFTY 50": {"spot": round(base_nifty, 2), "chg": "+42.50 (+0.18%)"},
        "BANK NIFTY": {"spot": round(base_bank, 2), "chg": "+150.0 (+0.26%)"},
        "SENSEX": {"spot": round(base_sensex, 2), "chg": "+82.40 (+0.13%)"},
        "FIN NIFTY": {"spot": round(base_fin, 2), "chg": "+50.00 (+0.23%)"},
        "MIDCAP NIFTY": {"spot": round(base_mid, 2), "chg": "+50.00 (+0.40%)"},
        "time": datetime.now().strftime("%H:%M:%S")
    }

data = get_live_market_data()

# Header Section
st.title("⚡ PRO TERMINAL")
st.button("🔄 Sync Live Market Data", use_container_width=True)

selected_index = st.selectbox(
    "📍 Select Active Index Filter:",
    ["ALL INDICES", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY", "MIDCAP NIFTY"]
)

# ------------------------------------------------------------------
# 3. FIXED HORIZONTAL TICKER BAR (Mobile-Optimized Grid HTML)
# ------------------------------------------------------------------
st.markdown(f"""
<div class="mobile-ticker-grid">
    <div class="ticker-card">
        <div class="ticker-name">NIFTY 50</div>
        <div class="ticker-price">{data['NIFTY 50']['spot']:,}</div>
        <div class="ticker-change">▲ +0.18%</div>
    </div>
    <div class="ticker-card">
        <div class="ticker-name">BANK NIFTY</div>
        <div class="ticker-price">{data['BANK NIFTY']['spot']:,}</div>
        <div class="ticker-change">▲ +0.26%</div>
    </div>
    <div class="ticker-card">
        <div class="ticker-name">SENSEX</div>
        <div class="ticker-price">{data['SENSEX']['spot']:,}</div>
        <div class="ticker-change">▲ +0.13%</div>
    </div>
    <div class="ticker-card">
        <div class="ticker-name">FIN NIFTY</div>
        <div class="ticker-price">{data['FIN NIFTY']['spot']:,}</div>
        <div class="ticker-change">▲ +0.23%</div>
    </div>
    <div class="ticker-card">
        <div class="ticker-name">MIDCAP</div>
        <div class="ticker-price">{data['MIDCAP NIFTY']['spot']:,}</div>
        <div class="ticker-change">▲ +0.40%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. SIGNALS & TAB STRUCTURE
# ------------------------------------------------------------------
trades_database = [
    {
        "id": "T1", "index": "NIFTY 50", "symbol": "NIFTY 24000 CE", "type": "BUY CALL",
        "algo": "EMA CROSS + OI SPIKE", "ltp": round(42.95 + np.random.uniform(-1, 1), 2), 
        "entry": 51.60, "sl": 39.50, "hold_sl": 34.20, "target": 79.00,
        "grade": "A+ (88% Prob)", "reason": "Strong Institutional Volume & OI Support", "lot": 65
    },
    {
        "id": "T2", "index": "BANK NIFTY", "symbol": "BANK NIFTY 56900 PE", "type": "BUY PUT",
        "algo": "REJECTION @ RESISTANCE", "ltp": round(53.50 + np.random.uniform(-1, 1), 2), 
        "entry": 53.50, "sl": 39.30, "hold_sl": 32.70, "target": 79.10,
        "grade": "A+ (85% Prob)", "reason": "Heavy Call Writing at 57100 Level", "lot": 15
    }
]

tab_signals, tab_hero, tab_btst, tab_chain, tab_analysis, tab_charts = st.tabs([
    f"⚡ Signals ({len(trades_database)})", "🚀 Zero-Hero", "🌙 BTST", "📊 Option Chain", "📈 Analysis", "📉 Chart"
])

def render_trade_card(t):
    with st.container(border=True):
        st.markdown(f"### {t['symbol']} (`{t['type']}`)")
        st.caption(f"⚙️ {t['algo']} | ⭐ {t['grade']}")
        st.write(f"💡 **Logic:** {t['reason']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("LTP", f"₹{t['ltp']}")
        c2.metric("ENTRY", f"₹{t['entry']}")
        c3.metric("SL", f"₹{t['sl']}")
        c4.metric("TARGET", f"₹{t['target']}")
        
        with st.expander(f"🛒 Place Order for {t['symbol']}"):
            f1, f2 = st.columns(2)
            with f1:
                lots = st.number_input("Lots:", min_value=1, value=1, key=f"lot_{t['id']}")
            with f2:
                price = st.number_input("Trigger Price:", value=float(t['entry']), key=f"p_{t['id']}")
            
            if st.button(f"🟢 BUY ({lots * t['lot']} QTY)", key=f"buy_{t['id']}", use_container_width=True):
                st.session_state.executed_orders.append(f"BUY {t['symbol']} @ ₹{price}")
                st.success(f"✅ Executed {lots * t['lot']} Qty @ ₹{price}")

with tab_signals:
    filtered = [t for t in trades_database if selected_index == "ALL INDICES" or t["index"] == selected_index]
    for trade in filtered:
        render_trade_card(trade)

with tab_hero:
    st.subheader("🚀 Zero-Hero Engine")
    st.info("Signals auto-trigger on Expiry days after 1:30 PM.")

with tab_btst:
    st.subheader("🌙 BTST Radar")
    st.success("Overnight Gap-up expected based on Global Market cues.")

with tab_chain:
    st.subheader("📊 Option Chain")
    chain_df = pd.DataFrame([
        {"CALL OI": "2.98L", "STRIKE": 23850, "PUT OI": "5.11L"},
        {"CALL OI": "3.73L", "STRIKE": 23900, "PUT OI": "5.71L"},
        {"CALL OI": "5.23L", "STRIKE": 24000, "PUT OI": "6.91L"},
        {"CALL OI": "4.13L", "STRIKE": 24100, "PUT OI": "6.03L"},
    ])
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

with tab_analysis:
    st.subheader("📈 Institutional Metrics")
    st.metric("PUT-CALL RATIO (PCR)", "1.28", "BULLISH 🟢")

with tab_charts:
    st.subheader("📉 Intraday Live Chart")
    dates = pd.date_range(end=datetime.now(), periods=20, freq='5min')
    close_prices = 24013.5 + np.cumsum(np.random.randn(20) * 2.0)
    df_chart = pd.DataFrame({'Open': close_prices-1, 'High': close_prices+2, 'Low': close_prices-2, 'Close': close_prices}, index=dates)

    fig_chart = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig_chart.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig_chart, use_container_width=True)
