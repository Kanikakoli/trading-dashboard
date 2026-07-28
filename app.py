import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v8.0 | Multi-Trade Edition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# SECURITY & PASSCODE LOCK
# ------------------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_passcode():
    if st.session_state.get("passcode_input") == "1234":
        st.session_state.authenticated = True
    else:
        st.error("❌ Invalid Passcode")

if not st.session_state.authenticated:
    st.title("🔐 Secure Terminal Access")
    st.text_input("Enter Passcode:", type="password", key="passcode_input", on_change=check_passcode)
    st.stop()

# ------------------------------------------------------------------
# COLORFUL LIGHT THEME CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #F4F6F9;
        color: #1F2937;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .ticker-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .ticker-name { font-size: 11px; color: #6B7280; font-weight: 700; }
    .ticker-price { font-size: 15px; font-weight: 800; color: #111827; margin: 2px 0; }
    .ticker-up { color: #059669; font-weight: 700; font-size: 11px; }
    .ticker-down { color: #DC2626; font-weight: 700; font-size: 11px; }

    .signal-card-bull {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.12);
    }

    .signal-card-bear {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 2px solid #EF4444;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.12);
    }

    .badge-giant {
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 800;
    }
    .badge-call { background-color: #10B981; color: #FFFFFF; }
    .badge-put { background-color: #EF4444; color: #FFFFFF; }

    .metric-subcard {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }

    .sentiment-box, .action-guidance-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DYNAMIC EXPIRY CALCULATOR
# ------------------------------------------------------------------
def get_next_weekday(weekday_idx):
    today = datetime.now()
    days_ahead = weekday_idx - today.weekday()
    if days_ahead < 0:  
        days_ahead += 7
    return today + timedelta(days=days_ahead)

# ------------------------------------------------------------------
# HEADER & INDEX SELECTOR
# ------------------------------------------------------------------
title_col, index_col = st.columns([2, 1])
with title_col:
    st.title("📊 MULTI-TRADE PRO TERMINAL v8.0")
with index_col:
    selected_index = st.selectbox(
        "🎯 Select Active Index:",
        ["NIFTY 50 (Lot Size: 65)", "BANK NIFTY (Lot Size: 15)", "FINNIFTY (Lot Size: 25)", "SENSEX (Lot Size: 10)"],
        index=0
    )

if "BANK NIFTY" in selected_index:
    lot_size = 15
    expiry_date = get_next_weekday(1).strftime("%d %b %Y (Tuesday)")
elif "FINNIFTY" in selected_index:
    lot_size = 25
    expiry_date = get_next_weekday(1).strftime("%d %b %Y (Tuesday)")
elif "SENSEX" in selected_index:
    lot_size = 10
    expiry_date = get_next_weekday(3).strftime("%d %b %Y (Thursday)")
else:
    lot_size = 65
    expiry_date = get_next_weekday(1).strftime("%d %b %Y (Tuesday)")

st.success(f"📅 **Active Weekly Expiry:** `{expiry_date}` | **Lot Size:** `{lot_size}`")

# ------------------------------------------------------------------
# 1. GLOBAL MARKET TICKERS
# ------------------------------------------------------------------
g1, g2, g3, g4, g5, g6 = st.columns(6)
globals_data = [
    ("GIFT NIFTY", "24,380.00", "▲ +120.00", "ticker-up", g1),
    ("S&P 500", "5,560.20", "▲ +34.50", "ticker-up", g2),
    ("NASDAQ", "18,240.10", "▲ +180.20", "ticker-up", g3),
    ("NIKKEI 225", "38,910.50", "▼ -45.00", "ticker-down", g4),
    ("HANG SENG", "17,650.00", "▲ +85.30", "ticker-up", g5),
    ("INDIA VIX", "13.20", "▼ -2.40%", "ticker-down", g6)
]

for name, val, change, tag, col in globals_data:
    with col:
        st.markdown(f"""
<div class="ticker-box">
    <div class="ticker-name">{name}</div>
    <div class="ticker-price">{val}</div>
    <div class="{tag}">{change}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. MULTI-TRADE ENGINE & SIDEBAR METRICS
# ------------------------------------------------------------------
col_left, col_right = st.columns([1.3, 1])

with col_left:
    analysis_mode = st.radio(
        "⚙️ Select Engine View:",
        ["🤖 Auto Multi-Signal Dashboard", "✍️ Custom Portfolio Manager"],
        horizontal=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # MODE 1: MULTIPLE SIGNALS DASHBOARD
    # ------------------------------------------------------------------
    if "Auto Multi-Signal" in analysis_mode:
        st.markdown("### ⚡ Live Signal Queue (Multiple Opportunities)")

        trades = [
            {
                "symbol": "NIFTY 24300 CE",
                "type": "BUY CALL",
                "badge_class": "badge-call",
                "card_class": "signal-card-bull",
                "entry": 110.0, "sl": 90.0, "target": 150.0,
                "reason": "Heavy Put Writing @ 24300 + VWAP Breakout",
                "lot_size": 65
            },
            {
                "symbol": "BANKNIFTY 52200 PE",
                "type": "BUY PUT",
                "badge_class": "badge-put",
                "card_class": "signal-card-bear",
                "entry": 240.0, "sl": 200.0, "target": 320.0,
                "reason": "Call Writing Barrier @ 52500 + Bearish Divergence",
                "lot_size": 15
            },
            {
                "symbol": "SENSEX 80100 CE",
                "type": "BUY CALL",
                "badge_class": "badge-call",
                "card_class": "signal-card-bull",
                "entry": 310.0, "sl": 260.0, "target": 410.0,
                "reason": "Expiry Gamma Squeeze + Short Covering",
                "lot_size": 10
            }
        ]

        for t in trades:
            risk = t['entry'] - t['sl']
            reward = t['target'] - t['entry']
            rr = reward / risk if risk > 0 else 0
            
            st.markdown(f"""
<div class="{t['card_class']}">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span class="badge-giant {t['badge_class']}">{t['type']}</span>
        <span style="font-weight: 700; font-size: 12px; color: #374151;">RR Ratio: <b>1:{rr:.1f}</b></span>
    </div>
    <h2 style="font-size: 22px; font-weight: 800; color: #111827; margin: 0 0 4px 0;">{t['symbol']}</h2>
    <p style="font-size: 12px; font-weight: 600; color: #4B5563; margin-bottom: 12px;">⚡ Trigger: {t['reason']}</p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
        <div class="metric-subcard">
            <div style="font-size: 10px; color: #6B7280; font-weight:700;">STOP LOSS</div>
            <div style="font-size: 16px; font-weight: 900; color: #DC2626;">₹{t['sl']:.1f}</div>
        </div>
        <div class="metric-subcard">
            <div style="font-size: 10px; color: #2563EB; font-weight:700;">BUY ENTRY</div>
            <div style="font-size: 16px; font-weight: 900; color: #111827;">₹{t['entry']:.1f}</div>
        </div>
        <div class="metric-subcard">
            <div style="font-size: 10px; color: #6B7280; font-weight:700;">TARGET</div>
            <div style="font-size: 16px; font-weight: 900; color: #059669;">₹{t['target']:.1f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # MODE 2: CUSTOM PORTFOLIO MANAGER (ADD MULTIPLE TRADES)
    # ------------------------------------------------------------------
    else:
        st.markdown("### ✍️ Build Your Multi-Trade Portfolio")
        
        if 'custom_trades' not in st.session_state:
            st.session_state.custom_trades = []

        with st.form("add_trade_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                t_symbol = st.text_input("Strike/Option", "NIFTY 24400 CE")
            with c2:
                t_entry = st.number_input("Entry Price (₹)", value=100.0, step=5.0)
            with c3:
                t_sl = st.number_input("SL Points (₹)", value=20.0, step=2.0)
            with c4:
                t_target = st.number_input("Target Points (₹)", value=40.0, step=5.0)

            c_lots = st.number_input("Lots", value=2, step=1)
            submitted = st.form_submit_button("➕ Add Trade to Basket")

            if submitted:
                st.session_state.custom_trades.append({
                    "Symbol": t_symbol,
                    "Lots": c_lots,
                    "Qty": c_lots * lot_size,
                    "Entry": t_entry,
                    "Total Investment": c_lots * lot_size * t_entry,
                    "Max Risk (₹)": c_lots * lot_size * t_sl,
                    "Max Profit (₹)": c_lots * lot_size * t_target
                })
                st.success(f"Added {t_symbol} to Basket!")

        if st.session_state.custom_trades:
            st.markdown("#### 🛒 Active Trade Basket")
            df = pd.DataFrame(st.session_state.custom_trades)
            st.dataframe(df, use_container_width=True)

            tot_risk = df["Max Risk (₹)"].sum()
            tot_profit = df["Max Profit (₹)"].sum()
            tot_invested = df["Total Investment"].sum()

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Capital Used", f"₹{tot_invested:,.2f}")
            m2.metric("Total Portfolio Risk", f"₹{tot_risk:,.2f}")
            m3.metric("Total Profit Target", f"₹{tot_profit:,.2f}")

            if st.button("🗑️ Clear Basket"):
                st.session_state.custom_trades = []
                st.rerun()

# ------------------------------------------------------------------
# 3. RIGHT SIDE: PCR, ADVANCE-DECLINE & TIMING GUIDE
# ------------------------------------------------------------------
with col_right:
    st.markdown("#### 📊 MARKET BREADTH (PCR & A/D)")
    st.markdown("""
<div class="sentiment-box">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
        <span style="font-size: 13px; font-weight: 700; color: #374151;">Put-Call Ratio (PCR):</span>
        <span style="font-size: 14px; font-weight: 800; color: #059669;">1.28 (BULLISH)</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
        <span style="font-size: 13px; font-weight: 700; color: #374151;">Advance / Decline Ratio:</span>
        <span style="font-size: 14px; font-weight: 800; color: #2563EB;">38 Advances / 12 Declines</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <span style="font-size: 13px; font-weight: 700; color: #374151;">Max Pain Strike:</span>
        <span style="font-size: 14px; font-weight: 800; color: #9333EA;">24,300 CE</span>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ⏰ TRADING EXECUTION GUIDE")
    st.markdown("""
<div class="action-guidance-box">
    <p style="margin: 0 0 8px 0; font-size: 12px; color: #1F2937;"><b>🟢 9:15 - 10:00 AM (WAIT):</b> Let opening high/low ranges settle before taking trade 1.</p>
    <p style="margin: 0 0 8px 0; font-size: 12px; color: #1F2937;"><b>🚀 1:30 PM+ (BUY WINDOW):</b> Best time window for Expiry day Zero-Hero options.</p>
    <p style="margin: 0 0 8px 0; font-size: 12px; color: #1F2937;"><b>🛡️ HOLD RULE:</b> Hold active trade while price trades above the VWAP level.</p>
    <p style="margin: 0; font-size: 12px; color: #1F2937;"><b>⏳ 2:45 PM+ (SQUARE OFF):</b> Mandatory exit time for all intraday positions.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. CHART OVERVIEW
# ------------------------------------------------------------------
st.divider()
st.markdown("#### 📈 LIVE MULTI-ASSET CANDLESTICK CHART")

dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="5min")
close_prices = np.cumsum(np.random.randn(30) * 1.5) + 24310
open_prices = close_prices + np.random.randn(30) * 2
high_prices = np.maximum(open_prices, close_prices) + np.random.rand(30) * 5
low_prices = np.minimum(open_prices, close_prices) - np.random.rand(30) * 5

fig = go.Figure(data=[go.Candlestick(
    x=dates, open=open_prices, high=high_prices, low=low_prices, close=close_prices,
    name="Index", increasing_line_color='#10B981', decreasing_line_color='#EF4444'
)])

fig.update_layout(
    template="plotly_white",
    height=320,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# LOCK TERMINAL
# ------------------------------------------------------------------
st.markdown("---")
if st.button("🔒 Lock Terminal"):
    st.session_state.authenticated = False
    st.rerun()

