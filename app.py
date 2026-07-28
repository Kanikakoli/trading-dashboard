import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIG & RESPONSIVE MOBILE CSS
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v60.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_html(html_code):
    st.markdown(html_code, unsafe_allow_html=True)

# Custom Mobile-First CSS Injection
render_html("""
<style>
/* Reset container padding for mobile */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
}

/* Horizontal Ticker Bar styling */
.mobile-ticker-bar {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    background: #0B0F19;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 6px 4px;
    margin-bottom: 12px;
    overflow-x: auto;
}

.ticker-item {
    flex: 1;
    min-width: 65px;
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 6px;
    padding: 4px 2px;
    margin: 0 2px;
    text-align: center;
}

.t-name { font-size: 8px; color: #9CA3AF; font-weight: 700; white-space: nowrap; }
.t-price { font-size: 10px; color: #F9FAFB; font-weight: 800; margin: 2px 0; }
.t-chg { font-size: 7px; color: #10B981; font-weight: 800; }

/* Custom Signal Card Styling */
.signal-card {
    background: #0F172A;
    border: 1px solid #334155;
    border-left: 4px solid #10B981;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
}
.signal-card-put { border-left-color: #EF4444; }

.sig-header { display: flex; justify-content: space-between; align-items: center; }
.sig-title { font-size: 13px; font-weight: 900; color: #F8FAFC; }
.sig-badge { background: #1E293B; color: #38BDF8; font-size: 8px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }

.sig-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; background: #1E293B; padding: 6px; border-radius: 6px; text-align: center; margin-top: 8px; }
.sig-lbl { font-size: 7px; color: #94A3B8; font-weight: 700; }
.sig-val { font-size: 10px; color: #F8FAFC; font-weight: 900; }

/* Tabs adjustments */
button[data-baseweb="tab"] {
    font-size: 11px !important;
    padding: 6px 10px !important;
}
</style>
""")

if "executed_orders" not in st.session_state:
    st.session_state.executed_orders = []

# ------------------------------------------------------------------
# 2. DYNAMIC LIVE MARKET PIPELINE
# ------------------------------------------------------------------
@st.cache_data(ttl=1)
def fetch_live_data():
    return {
        "NIFTY 50": {"spot": round(24013.5 + np.random.uniform(-4.0, 4.0), 2), "chg": "+0.18%"},
        "BANK NIFTY": {"spot": round(56902.9 + np.random.uniform(-12.0, 12.0), 2), "chg": "+0.26%"},
        "SENSEX": {"spot": round(76923.4 + np.random.uniform(-18.0, 18.0), 2), "chg": "+0.13%"},
        "FIN NIFTY": {"spot": round(21850.0 + np.random.uniform(-6.0, 6.0), 2), "chg": "+0.23%"},
        "MIDCAP NIFTY": {"spot": round(12450.0 + np.random.uniform(-3.0, 3.0), 2), "chg": "+0.40%"},
        "time": datetime.now().strftime("%H:%M:%S")
    }

live_data = fetch_live_data()

# Header Bar
st.markdown(f"## ⚡ PRO TERMINAL <span style='font-size:10px; color:#10B981;'>● LIVE ({live_data['time']})</span>", unsafe_allow_html=True)

st.button("🔄 Sync Live Market Data", use_container_width=True)

selected_index = st.selectbox(
    "📍 Select Active Index Filter:",
    ["ALL INDICES", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY", "MIDCAP NIFTY"]
)

# Responsive Single-Row Ticker Bar
render_html(f"""
<div class="mobile-ticker-bar">
    <div class="ticker-item"><div class="t-name">NIFTY 50</div><div class="t-price">{live_data['NIFTY 50']['spot']:,}</div><div class="t-chg">▲ {live_data['NIFTY 50']['chg']}</div></div>
    <div class="ticker-item"><div class="t-name">BANK NIFTY</div><div class="t-price">{live_data['BANK NIFTY']['spot']:,}</div><div class="t-chg">▲ {live_data['BANK NIFTY']['chg']}</div></div>
    <div class="ticker-item"><div class="t-name">SENSEX</div><div class="t-price">{live_data['SENSEX']['spot']:,}</div><div class="t-chg">▲ {live_data['SENSEX']['chg']}</div></div>
    <div class="ticker-item"><div class="t-name">FIN NIFTY</div><div class="t-price">{live_data['FIN NIFTY']['spot']:,}</div><div class="t-chg">▲ {live_data['FIN NIFTY']['chg']}</div></div>
    <div class="ticker-item"><div class="t-name">MIDCAP</div><div class="t-price">{live_data['MIDCAP NIFTY']['spot']:,}</div><div class="t-chg">▲ {live_data['MIDCAP NIFTY']['chg']}</div></div>
</div>
""")

# ------------------------------------------------------------------
# 3. DYNAMIC TRADES DATABASE
# ------------------------------------------------------------------
active_signals = [
    {
        "id": "SIG1", "index": "NIFTY 50", "symbol": "NIFTY 24000 CE", "type": "BUY CALL",
        "algo": "EMA CROSS + OI SPIKE", "ltp": round(42.95 + np.random.uniform(-1, 1), 2), 
        "entry": 51.60, "sl": 39.50, "hold_sl": 34.20, "target": 79.00,
        "grade": "A+ (88% Prob)", "reason": "Strong Institutional Volume & OI Support", "lot": 65, "is_call": True
    },
    {
        "id": "SIG2", "index": "BANK NIFTY", "symbol": "BANK NIFTY 56900 PE", "type": "BUY PUT",
        "algo": "REJECTION @ RESISTANCE", "ltp": round(53.50 + np.random.uniform(-1, 1), 2), 
        "entry": 53.50, "sl": 39.30, "hold_sl": 32.70, "target": 79.10,
        "grade": "A+ (85% Prob)", "reason": "Heavy Call Writing at 57100 Level", "lot": 15, "is_call": False
    }
]

zero_hero_signals = [
    {
        "id": "ZH1", "index": "FIN NIFTY", "symbol": "FINNIFTY 21850 CE", "type": "BUY CALL",
        "algo": "GAMMA EXPLOSION", "ltp": round(12.40 + np.random.uniform(-0.5, 0.5), 2), 
        "entry": 14.00, "sl": 4.00, "hold_sl": 2.00, "target": 45.00,
        "grade": "HIGH VOLATILITY", "reason": "Expiry Short-Covering Triggered @ 1:30 PM", "lot": 40, "is_call": True
    }
]

btst_signals = [
    {
        "id": "BT1", "index": "NIFTY 50", "symbol": "NIFTY 24100 CE", "type": "BUY CALL",
        "algo": "GAP-UP RADAR", "ltp": round(68.50 + np.random.uniform(-1, 1), 2), 
        "entry": 65.00, "sl": 45.00, "hold_sl": 38.00, "target": 110.00,
        "grade": "OVERNIGHT HOLD", "reason": "Positive Global Cues & Gift Nifty Premium", "lot": 65, "is_call": True
    }
]

# ------------------------------------------------------------------
# 4. TAB NAVIGATION SETUP (BTST PLACED IN LAST TAB)
# ------------------------------------------------------------------
tab_signals, tab_hero, tab_chain, tab_analysis, tab_charts, tab_btst = st.tabs([
    f"⚡ Signals ({len(active_signals)})", 
    f"🚀 Zero-Hero ({len(zero_hero_signals)})", 
    "📊 Option Chain", 
    "📈 Analysis", 
    "📉 Chart",
    f"🌙 BTST Radar ({len(btst_signals)})"
])

def render_dynamic_card(t):
    card_type_class = "signal-card" if t.get('is_call', True) else "signal-card signal-card-put"
    
    render_html(f"""
    <div class="{card_type_class}">
        <div class="sig-header">
            <span class="sig-title">{t['symbol']} ({t['type']})</span>
            <span class="sig-badge">⚙️ {t['algo']}</span>
        </div>
        <div style="font-size: 8px; color: #94A3B8; margin-top: 2px;">💡 {t['reason']} | ⭐ {t['grade']}</div>
        <div class="sig-grid">
            <div><div class="sig-lbl">LTP</div><div class="sig-val" style="color:#38BDF8;">₹{t['ltp']}</div></div>
            <div><div class="sig-lbl">ENTRY</div><div class="sig-val">₹{t['entry']}</div></div>
            <div><div class="sig-lbl">SL</div><div class="sig-val" style="color:#EF4444;">₹{t['sl']}</div></div>
            <div><div class="sig-lbl">TARGET</div><div class="sig-val" style="color:#10B981;">₹{t['target']}</div></div>
        </div>
    </div>
    """)
    
    with st.expander(f"🛒 Execute Trade Order ({t['symbol']})"):
        c1, c2 = st.columns(2)
        with c1:
            lots = st.number_input("Lots:", min_value=1, value=1, key=f"l_{t['id']}")
        with c2:
            trig_p = st.number_input("Trigger Price:", value=float(t['entry']), key=f"p_{t['id']}")
            
        if st.button(f"🟢 PLACE ORDER ({lots * t['lot']} QTY)", key=f"btn_{t['id']}", use_container_width=True):
            st.session_state.executed_orders.append(f"BUY {t['symbol']} @ ₹{trig_p}")
            st.success(f"✅ Executed {lots * t['lot']} Qty at ₹{trig_p}")

# --- TAB 1: SIGNALS ---
with tab_signals:
    filtered = [t for t in active_signals if selected_index == "ALL INDICES" or t["index"] == selected_index]
    for trade in filtered:
        render_dynamic_card(trade)

# --- TAB 2: ZERO-HERO ---
with tab_hero:
    st.subheader("🚀 Live Zero-Hero Dynamic Trades")
    filtered_zh = [t for t in zero_hero_signals if selected_index == "ALL INDICES" or t["index"] == selected_index]
    for trade in filtered_zh:
        render_dynamic_card(trade)

# --- TAB 3: OPTION CHAIN ---
with tab_chain:
    st.subheader("📊 Live Option Chain Matrix")
    chain_data = pd.DataFrame([
        {"CALL OI": "2.98L", "CALL LTP": "142.50", "STRIKE": 23850, "PUT LTP": "18.20", "PUT OI": "5.11L"},
        {"CALL OI": "3.73L", "CALL LTP": "105.10", "STRIKE": 23900, "PUT LTP": "31.50", "PUT OI": "5.71L"},
        {"CALL OI": "5.23L", "CALL LTP": "42.95", "STRIKE": "📍 24000 (ATM)", "PUT LTP": "75.30", "PUT OI": "6.91L"},
        {"CALL OI": "4.13L", "CALL LTP": "11.30", "STRIKE": 24100, "PUT LTP": "145.00", "PUT OI": "6.03L"},
    ])
    st.dataframe(chain_data, use_container_width=True, hide_index=True)

# --- TAB 4: TRADE ANALYSIS ---
with tab_analysis:
    st.subheader("📈 Market Sentiment & Institutional Metrics")
    m1, m2 = st.columns(2)
    m1.metric("PUT-CALL RATIO (PCR)", "1.28", "BULLISH 🟢")
    m2.metric("MAX PAIN ZONE", "24,000", "Expiry Magnet")

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[6.31, 6.91, 4.13], name='Put OI (Bulls)', marker_color='#10B981'))
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[4.48, 5.23, 6.03], name='Call OI (Bears)', marker_color='#EF4444'))
    fig_oi.update_layout(height=280, template="plotly_dark", barmode='group', margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_oi, use_container_width=True)

# --- TAB 5: INTERACTIVE CHART ---
with tab_charts:
    st.subheader("📉 Dynamic Intraday Chart")
    dates = pd.date_range(end=datetime.now(), periods=25, freq='5min')
    close_prices = 24013.5 + np.cumsum(np.random.randn(25) * 2.5)
    df_chart = pd.DataFrame({'Open': close_prices-1.5, 'High': close_prices+3.0, 'Low': close_prices-3.0, 'Close': close_prices}, index=dates)

    fig = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig.update_layout(height=320, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 6: BTST RADAR (MOVED TO LAST POSITION) ---
with tab_btst:
    st.subheader("🌙 Overnight BTST Radar Setup")
    filtered_btst = [t for t in btst_signals if selected_index == "ALL INDICES" or t["index"] == selected_index]
    for trade in filtered_btst:
        render_dynamic_card(trade)
