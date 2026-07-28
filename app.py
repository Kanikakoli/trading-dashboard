import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v10.0 | Full Levels Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# SECURITY LOCK
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

def render_clean_html(html_str):
    st.markdown(html_str.strip(), unsafe_allow_html=True)

# ------------------------------------------------------------------
# COMPACT STYLE
# ------------------------------------------------------------------
render_clean_html("""
<style>
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}
.ticker-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: space-between;
    margin-bottom: 10px;
}
.ticker-chip {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 6px 8px;
    flex: 1 1 calc(20% - 6px);
    min-width: 85px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.chip-title { font-size: 9px; color: #64748B; font-weight: 700; text-transform: uppercase; }
.chip-val { font-size: 11px; font-weight: 800; color: #0F172A; }
.chip-up { font-size: 9px; color: #10B981; font-weight: 700; }
.chip-down { font-size: 9px; color: #EF4444; font-weight: 700; }

.status-banner {
    background: #0F172A;
    color: #FFFFFF;
    padding: 10px 14px;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.status-pill-bullish { background: #059669; color: #FFF; padding: 3px 8px; border-radius: 20px; font-weight: 800; font-size: 10px; }
.status-pill-hz { background: #7C3AED; color: #FFF; padding: 3px 8px; border-radius: 20px; font-weight: 800; font-size: 10px; }

/* Levels Card Styling */
.levels-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
}
.level-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    margin-top: 6px;
    text-align: center;
}
.s-box { background: #DCFCE7; border-radius: 6px; padding: 4px; }
.r-box { background: #FEE2E2; border-radius: 6px; padding: 4px; }
.level-lbl { font-size: 9px; font-weight: 800; }
.level-val { font-size: 12px; font-weight: 800; color: #0F172A; }

.compact-trade-card {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.card-call-border { border-left: 6px solid #10B981; }
.card-put-border { border-left: 6px solid #EF4444; }
.card-hz-border { border-left: 6px solid #8B5CF6; }

.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.strike-title { font-size: 15px; font-weight: 800; color: #0F172A; margin: 0; }
.badge-pill-call { background: #D1FAE5; color: #065F46; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 12px; }
.badge-pill-put { background: #FEE2E2; color: #991B1B; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 12px; }
.badge-pill-hz { background: #DDD6FE; color: #5B21B6; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 12px; }

.valid-tag { background: #DCFCE7; color: #15803D; font-size: 9px; font-weight: 800; padding: 2px 5px; border-radius: 4px; }
.expired-tag { background: #FEE2E2; color: #B91C1C; font-size: 9px; font-weight: 800; padding: 2px 5px; border-radius: 4px; }

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    background: #F8FAFC;
    padding: 8px;
    border-radius: 8px;
    text-align: center;
    margin-top: 8px;
}
.m-label { font-size: 9px; color: #64748B; font-weight: 700; }
.m-val { font-size: 12px; font-weight: 800; color: #0F172A; }
.m-sub-up { font-size: 9px; color: #10B981; font-weight: 700; }
.m-sub-down { font-size: 9px; color: #EF4444; font-weight: 700; }

.rr-bar-container {
    height: 8px;
    width: 100%;
    background: #E2E8F0;
    border-radius: 4px;
    display: flex;
    overflow: hidden;
    margin-top: 8px;
}
.rr-risk { background: #EF4444; height: 100%; }
.rr-reward { background: #10B981; height: 100%; }
</style>
""")

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚡ Settings")
    if st.button("🔒 Lock Terminal", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.title("⚡ PRO TERMINAL v10.0")

# ------------------------------------------------------------------
# 1. GLOBAL & STOCKS TICKERS
# ------------------------------------------------------------------
render_clean_html("""
<div class="ticker-bar">
    <div class="ticker-chip"><div class="chip-title">GIFT NIFTY</div><div class="chip-val">24,380</div><div class="chip-up">▲ +120</div></div>
    <div class="ticker-chip"><div class="chip-title">GOLD (10g)</div><div class="chip-val">₹72,450</div><div class="chip-up">▲ +210</div></div>
    <div class="ticker-chip"><div class="chip-title">SILVER (1kg)</div><div class="chip-val">₹88,200</div><div class="chip-down">▼ -340</div></div>
    <div class="ticker-chip"><div class="chip-title">INDIA VIX</div><div class="chip-val">13.20</div><div class="chip-down">▼ -2.4%</div></div>
    <div class="ticker-chip"><div class="chip-title">RELIANCE</div><div class="chip-val">₹2,980</div><div class="chip-up">▲ +1.2%</div></div>
    <div class="ticker-chip"><div class="chip-title">HDFCBANK</div><div class="chip-val">₹1,640</div><div class="chip-up">▲ +0.8%</div></div>
    <div class="ticker-chip"><div class="chip-title">ICICIBANK</div><div class="chip-val">₹1,210</div><div class="chip-down">▼ -0.3%</div></div>
    <div class="ticker-chip"><div class="chip-title">TCS</div><div class="chip-val">₹4,250</div><div class="chip-up">▲ +1.5%</div></div>
    <div class="ticker-chip"><div class="chip-title">INFY</div><div class="chip-val">₹1,780</div><div class="chip-up">▲ +0.6%</div></div>
</div>
""")

# ------------------------------------------------------------------
# 2. STATUS BANNER
# ------------------------------------------------------------------
now = datetime.now()
last_update = now.strftime("%H:%M:%S")
next_update = (now + timedelta(minutes=15)).strftime("%H:%M:%S")

render_clean_html(f"""
<div class="status-banner">
    <div>
        <div style="font-size: 10px; color: #94A3B8; font-weight: 700;">LIVE MARKET TREND</div>
        <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
            <span class="status-pill-bullish">🟢 BULLISH BREAKOUT</span>
            <span class="status-pill-hz">🔥 HERO-ZERO ACTIVE</span>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 10px; color: #94A3B8;">Last Update: <b style="color:#FFF;">{last_update}</b></div>
        <div style="font-size: 10px; color: #94A3B8;">Next Refresh: <b style="color:#F59E0B;">{next_update}</b></div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 3. INDICES SUPPORTS & RESISTANCES SECTION
# ------------------------------------------------------------------
st.caption("🎯 Major Indices Key Pivots, Supports & Resistances")

levels_data = [
    {"index": "NIFTY 50", "spot": "24,380.5", "s2": "24,200", "s1": "24,300", "r1": "24,450", "r2": "24,550"},
    {"index": "BANK NIFTY", "spot": "52,340.2", "s2": "51,800", "s1": "52,000", "r1": "52,600", "r2": "53,000"},
    {"index": "SENSEX", "spot": "80,120.0", "s2": "79,500", "s1": "79,800", "r1": "80,400", "r2": "80,800"}
]

cols = st.columns(3)
for i, lvl in enumerate(levels_data):
    with cols[i]:
        render_clean_html(f"""
        <div class="levels-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px; font-weight: 800; color: #0F172A;">{lvl['index']}</span>
                <span style="font-size: 11px; font-weight: 700; color: #059669;">{lvl['spot']}</span>
            </div>
            <div class="level-grid">
                <div class="s-box"><div class="level-lbl" style="color: #15803D;">S2</div><div class="level-val">{lvl['s2']}</div></div>
                <div class="s-box"><div class="level-lbl" style="color: #15803D;">S1</div><div class="level-val">{lvl['s1']}</div></div>
                <div class="r-box"><div class="level-lbl" style="color: #B91C1C;">R1</div><div class="level-val">{lvl['r1']}</div></div>
                <div class="r-box"><div class="level-lbl" style="color: #B91C1C;">R2</div><div class="level-val">{lvl['r2']}</div></div>
            </div>
        </div>
        """)

# ------------------------------------------------------------------
# 4. MAIN TABS
# ------------------------------------------------------------------
tab_signals, tab_oi, tab_charts, tab_basket = st.tabs([
    "⚡ Active Signals", 
    "📊 OI & Writers", 
    "📈 Interactive Chart",
    "✍️ Multi-Trade Basket"
])

# ------------------------------------------------------------------
# TAB 1: SIGNALS
# ------------------------------------------------------------------
with tab_signals:
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        filter_index = st.selectbox("Index:", ["ALL", "NIFTY 50", "BANK NIFTY", "SENSEX"], label_visibility="collapsed")
    with col_f2:
        filter_type = st.selectbox("Type:", ["ALL SIGNALS", "HERO-ZERO ONLY", "INTRADAY SCALP"], label_visibility="collapsed")

    trades = [
        {
            "symbol": "SENSEX 80100 CE",
            "index": "SENSEX",
            "tag": "HERO-ZERO",
            "type": "BUY CALL",
            "entry": 25.0, "sl": 5.0, "target": 110.0,
            "reason": "🚀 Gamma Spike above R1 @ 80,400 Resistance",
            "lot_size": 10,
            "valid_till": (datetime.now() + timedelta(minutes=30)).strftime("%H:%M"),
            "is_valid": True
        },
        {
            "symbol": "NIFTY 24350 CE",
            "index": "NIFTY 50",
            "tag": "INTRADAY SCALP",
            "type": "BUY CALL",
            "entry": 110.0, "sl": 90.0, "target": 160.0,
            "reason": "Holding S1 Support @ 24,300 + VWAP Breakout",
            "lot_size": 65,
            "valid_till": (datetime.now() + timedelta(minutes=45)).strftime("%H:%M"),
            "is_valid": True
        }
    ]

    filtered_trades = [
        t for t in trades 
        if (filter_index == "ALL" or t["index"] == filter_index) and
           (filter_type == "ALL SIGNALS" or (filter_type == "HERO-ZERO ONLY" and t["tag"] == "HERO-ZERO") or (filter_type == "INTRADAY SCALP" and t["tag"] == "INTRADAY SCALP"))
    ]

    for t in filtered_trades:
        risk = t['entry'] - t['sl']
        reward = t['target'] - t['entry']
        rr = reward / risk if risk > 0 else 1
        
        is_hz = t['tag'] == "HERO-ZERO"
        is_call = "CALL" in t['type']

        card_border = "card-hz-border" if is_hz else ("card-call-border" if is_call else "card-put-border")
        badge_pill = "badge-pill-hz" if is_hz else ("badge-pill-call" if is_call else "badge-pill-put")
        validity_badge = f'<span class="valid-tag">✅ VALID ({t["valid_till"]})</span>' if t['is_valid'] else f'<span class="expired-tag">⚠️ EXPIRED</span>'

        total_range = risk + reward
        risk_pct = (risk / total_range) * 100
        reward_pct = (reward / total_range) * 100

        card_html = f"""<div class="compact-trade-card {card_border}">
<div class="card-header-flex">
<div><span class="{badge_pill}">{t['tag']}</span> <span style="font-size: 11px; font-weight: 700; color: #64748B;">RR 1:{rr:.1f}</span> {validity_badge}</div>
<div style="font-size: 10px; font-weight: 700; color: #475569;">Lot Size: {t['lot_size']}</div>
</div>
<div class="strike-title">{t['symbol']} ({t['type']})</div>
<div style="font-size: 11px; color: #475569; margin-top: 2px;">{t['reason']}</div>
<div class="metrics-grid">
<div><div class="m-label">ENTRY</div><div class="m-val">₹{t['entry']:.0f}</div></div>
<div><div class="m-label">STOP LOSS</div><div class="m-val">₹{t['sl']:.0f}</div><div class="m-sub-down">-₹{risk:.0f}</div></div>
<div><div class="m-label">TARGET</div><div class="m-val">₹{t['target']:.0f}</div><div class="m-sub-up">+₹{reward:.0f}</div></div>
<div><div class="m-label">LOT RISK</div><div class="m-val">₹{risk * t['lot_size']:,.0f}</div><div class="m-sub-up">T: ₹{reward * t['lot_size']:,.0f}</div></div>
</div>
<div class="rr-bar-container">
<div class="rr-risk" style="width: {risk_pct}%;"></div>
<div class="rr-reward" style="width: {reward_pct}%;"></div>
</div>
</div>"""
        
        render_clean_html(card_html)

# ------------------------------------------------------------------
# TAB 2: OI ANALYSIS
# ------------------------------------------------------------------
with tab_oi:
    st.caption("📊 Expiry Open Interest (Call vs Put Writers)")
    strikes = [24100, 24200, 24300, 24400, 24500]
    call_oi = [12.4, 25.1, 48.6, 85.2, 92.0]
    put_oi = [88.5, 95.2, 78.4, 32.1, 10.5]

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=strikes, y=call_oi, name='Call Writers (Resistance)', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=strikes, y=put_oi, name='Put Writers (Support)', marker_color='#10B981'))
    fig_oi.update_layout(barmode='group', height=260, margin=dict(l=5, r=5, t=5, b=5), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_oi, use_container_width=True)

# ------------------------------------------------------------------
# TAB 3: CHARTS WITH SUPPORT/RESISTANCE OVERLAY
# ------------------------------------------------------------------
with tab_charts:
    st.caption("📈 Nifty Candle Chart with S/R Lines + VWAP + RSI")
    
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=50, freq='5min')
    close_prices = 24300 + np.cumsum(np.random.randn(50) * 8)
    high_prices = close_prices + np.random.rand(50) * 12
    low_prices = close_prices - np.random.rand(50) * 12
    open_prices = low_prices + np.random.rand(50) * (high_prices - low_prices)

    df_chart = pd.DataFrame({'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices}, index=dates)

    df_chart['SMA20'] = df_chart['Close'].rolling(20).mean()
    df_chart['VWAP'] = (df_chart['Close'] * (df_chart['High'] + df_chart['Low'] + df_chart['Close'])/3).cumsum() / (df_chart['High'] + df_chart['Low'] + df_chart['Close']).cumsum()
    
    delta = df_chart['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df_chart['RSI'] = 100 - (100 / (1 + rs))

    fig_chart = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig_chart.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], name='Price'), row=1, col=1)
    
    # Adding Horizontal S/R Lines on Chart
    fig_chart.add_hline(y=24450, line_dash="dash", line_color="#EF4444", annotation_text="R1 24,450", row=1, col=1)
    fig_chart.add_hline(y=24300, line_dash="dash", line_color="#10B981", annotation_text="S1 24,300", row=1, col=1)

    fig_chart.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA20'], line=dict(color='orange', width=1), name='SMA20'), row=1, col=1)
    fig_chart.add_trace(go.Scatter(x=df_chart.index, y=df_chart['VWAP'], line=dict(color='purple', width=1.5, dash='dash'), name='VWAP'), row=1, col=1)
    fig_chart.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], line=dict(color='blue', width=1.5), name='RSI'), row=2, col=1)

    fig_chart.update_layout(height=380, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig_chart, use_container_width=True)

# ------------------------------------------------------------------
# TAB 4: BASKET BUILDER
# ------------------------------------------------------------------
with tab_basket:
    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    st.caption("✍️ Multi-Trade Basket / Hedging Builder")
    with st.form("compact_form"):
        f1, f2 = st.columns(2)
        with f1: t_symbol = st.text_input("Strike", "SENSEX 80200 CE")
        with f2: t_type = st.selectbox("Tag", ["HERO-ZERO", "INTRADAY", "HEDGE"])
        
        f3, f4, f5 = st.columns(3)
        with f3: t_entry = st.number_input("Entry (₹)", value=20.0)
        with f4: t_sl = st.number_input("SL Points", value=5.0)
        with f5: t_target = st.number_input("Target Points", value=80.0)
        
        submitted = st.form_submit_button("Add to Basket", use_container_width=True)

        if submitted:
            st.session_state.custom_trades.append({
                "Symbol": t_symbol,
                "Type": t_type,
                "Entry": t_entry,
                "Risk (₹)": 10 * t_sl,
                "Reward (₹)": 10 * t_target
            })
            st.success("Added!")

    if st.session_state.custom_trades:
        df = pd.DataFrame(st.session_state.custom_trades)
        st.dataframe(df, use_container_width=True)
        if st.button("Clear Basket", use_container_width=True):
            st.session_state.custom_trades = []
            st.rerun()
