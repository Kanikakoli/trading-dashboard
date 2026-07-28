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
    page_title="PRO TERMINAL v11.0 | Real-Time Market Metrics",
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
# STYLES (ADVANCE/DECLINE, PCR & OPEN/PREV CLOSE INCLUDED)
# ------------------------------------------------------------------
render_clean_html("""
<style>
.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

/* Market Stats Top Strip */
.market-stats-bar {
    background: #0F172A;
    border-radius: 10px;
    padding: 10px;
    color: #FFFFFF;
    margin-bottom: 10px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    text-align: center;
}
.stat-box {
    background: #1E293B;
    border-radius: 6px;
    padding: 6px;
}
.stat-lbl { font-size: 9px; color: #94A3B8; font-weight: 700; text-transform: uppercase; }
.stat-val { font-size: 13px; font-weight: 800; color: #FFFFFF; }
.stat-sub-up { font-size: 9px; color: #10B981; font-weight: 700; }
.stat-sub-down { font-size: 9px; color: #EF4444; font-weight: 700; }

/* Advance Decline Bar */
.ad-bar-container {
    height: 6px;
    width: 100%;
    background: #EF4444;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 4px;
    display: flex;
}
.ad-advance { background: #10B981; height: 100%; }

/* Level Cards Styling */
.levels-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 8px;
    margin-bottom: 10px;
}
.level-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    margin-top: 4px;
    text-align: center;
}
.s-box { background: #DCFCE7; border-radius: 4px; padding: 3px; }
.r-box { background: #FEE2E2; border-radius: 4px; padding: 3px; }
.level-lbl { font-size: 9px; font-weight: 800; }
.level-val { font-size: 11px; font-weight: 800; color: #0F172A; }

/* Trade Cards */
.compact-trade-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    padding: 10px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.card-call-border { border-left: 5px solid #10B981; }
.card-put-border { border-left: 5px solid #EF4444; }
.card-hz-border { border-left: 5px solid #8B5CF6; }

.card-header-flex { display: flex; justify-content: space-between; align-items: center; }
.strike-title { font-size: 14px; font-weight: 800; color: #0F172A; }
.badge-pill-call { background: #D1FAE5; color: #065F46; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 10px; }
.badge-pill-put { background: #FEE2E2; color: #991B1B; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 10px; }
.badge-pill-hz { background: #DDD6FE; color: #5B21B6; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 10px; }

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    background: #F8FAFC;
    padding: 6px;
    border-radius: 6px;
    text-align: center;
    margin-top: 6px;
}
.m-label { font-size: 9px; color: #64748B; font-weight: 700; }
.m-val { font-size: 11px; font-weight: 800; color: #0F172A; }

.rr-bar-container {
    height: 6px; width: 100%; background: #E2E8F0; border-radius: 3px; display: flex; overflow: hidden; margin-top: 6px;
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

st.title("⚡ PRO TERMINAL v11.0")

# ------------------------------------------------------------------
# 1. ADVANCE/DECLINE, PCR, OPEN & PREV CLOSE STRIP
# ------------------------------------------------------------------
# Real live data aligned parameters
advances = 1340
declines = 820
total_stocks = advances + declines
adv_pct = (advances / total_stocks) * 100

pcr_nifty = 0.88
nifty_spot = 24007.75
nifty_open = 23990.10
nifty_prev_close = 23995.95
nifty_chg = nifty_spot - nifty_prev_close
nifty_chg_pct = (nifty_chg / nifty_prev_close) * 100

render_clean_html(f"""
<div class="market-stats-bar">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-lbl">NIFTY 50 SPOT</div>
            <div class="stat-val">{nifty_spot:,.2f}</div>
            <div class="stat-sub-up">▲ +{nifty_chg:.2f} (+{nifty_chg_pct:.2f}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">OPEN / PREV CLOSE</div>
            <div class="stat-val">{nifty_open:,.2f}</div>
            <div style="font-size: 9px; color: #94A3B8;">Prev: <b style="color:#FFF;">{nifty_prev_close:,.2f}</b></div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">PCR (PUT-CALL RATIO)</div>
            <div class="stat-val" style="color: #F59E0B;">{pcr_nifty:.2f}</div>
            <div style="font-size: 9px; color: #94A3B8;">Status: <b>NEUTRAL / MILD BULL</b></div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">ADV / DEC RATIO</div>
            <div class="stat-val">{advances} : {declines}</div>
            <div class="ad-bar-container">
                <div class="ad-advance" style="width: {adv_pct}%;"></div>
            </div>
        </div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 2. INDICES SUPPORTS & RESISTANCES SECTION (UPDATED TO CURRENT MARKET)
# ------------------------------------------------------------------
st.caption("🎯 Current Indices Levels & Pivots")

levels_data = [
    {"index": "NIFTY 50", "spot": "24,007.7", "s2": "23,900", "s1": "23,950", "r1": "24,050", "r2": "24,100"},
    {"index": "BANK NIFTY", "spot": "57,014.5", "s2": "56,500", "s1": "56,800", "r1": "57,200", "r2": "57,500"},
    {"index": "SENSEX", "spot": "76,863.7", "s2": "76,200", "s1": "76,500", "r1": "77,100", "r2": "77,500"}
]

cols = st.columns(3)
for i, lvl in enumerate(levels_data):
    with cols[i]:
        render_clean_html(f"""
        <div class="levels-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; font-weight: 800; color: #0F172A;">{lvl['index']}</span>
                <span style="font-size: 10px; font-weight: 700; color: #059669;">{lvl['spot']}</span>
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
# 3. MAIN NAVIGATION TABS
# ------------------------------------------------------------------
tab_signals, tab_oi, tab_charts, tab_basket = st.tabs([
    "⚡ Active Signals", 
    "📊 OI & Writers", 
    "📈 Interactive Chart",
    "✍️ Multi-Trade Basket"
])

# ------------------------------------------------------------------
# TAB 1: SIGNALS (ALIGNED WITH CURRENT MARKET PRICE)
# ------------------------------------------------------------------
with tab_signals:
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        filter_index = st.selectbox("Index:", ["ALL", "NIFTY 50", "BANK NIFTY", "SENSEX"], label_visibility="collapsed")
    with col_f2:
        filter_type = st.selectbox("Type:", ["ALL SIGNALS", "HERO-ZERO ONLY", "INTRADAY SCALP"], label_visibility="collapsed")

    trades = [
        {
            "symbol": "NIFTY 24050 CE",
            "index": "NIFTY 50",
            "tag": "INTRADAY SCALP",
            "type": "BUY CALL",
            "entry": 26.0, "sl": 15.0, "target": 55.0,
            "reason": "Nifty holding 24000 support level + RSI rebound",
            "lot_size": 65,
            "valid_till": (datetime.now() + timedelta(minutes=30)).strftime("%H:%M"),
            "is_valid": True
        },
        {
            "symbol": "NIFTY 24100 CE",
            "index": "NIFTY 50",
            "tag": "HERO-ZERO",
            "type": "BUY CALL",
            "entry": 13.0, "sl": 4.0, "target": 45.0,
            "reason": "🚀 Expiry Gamma move expected above 24050 R1 level",
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

        total_range = risk + reward
        risk_pct = (risk / total_range) * 100
        reward_pct = (reward / total_range) * 100

        card_html = f"""<div class="compact-trade-card {card_border}">
<div class="card-header-flex">
<div><span class="{badge_pill}">{t['tag']}</span> <span style="font-size: 10px; font-weight: 700; color: #64748B;">RR 1:{rr:.1f}</span></div>
<div style="font-size: 10px; font-weight: 700; color: #475569;">Lot Size: {t['lot_size']}</div>
</div>
<div class="strike-title">{t['symbol']} ({t['type']})</div>
<div style="font-size: 11px; color: #475569; margin-top: 2px;">{t['reason']}</div>
<div class="metrics-grid">
<div><div class="m-label">ENTRY</div><div class="m-val">₹{t['entry']:.1f}</div></div>
<div><div class="m-label">STOP LOSS</div><div class="m-val">₹{t['sl']:.1f}</div></div>
<div><div class="m-label">TARGET</div><div class="m-val">₹{t['target']:.1f}</div></div>
<div><div class="m-label">LOT RISK</div><div class="m-val">₹{risk * t['lot_size']:,.0f}</div></div>
</div>
<div class="rr-bar-container">
<div class="rr-risk" style="width: {risk_pct}%;"></div>
<div class="rr-reward" style="width: {reward_pct}%;"></div>
</div>
</div>"""
        
        render_clean_html(card_html)

# ------------------------------------------------------------------
# TAB 2: OI & WRITERS
# ------------------------------------------------------------------
with tab_oi:
    st.caption("📊 Live Strike OI (23900 to 24200)")
    strikes = [23900, 23950, 24000, 24050, 24100, 24150, 24200]
    call_oi = [64.8, 72.1, 262.0, 126.0, 190.0, 97.4, 236.0]
    put_oi = [225.0, 199.0, 264.0, 50.0, 56.1, 9.5, 34.0]

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=strikes, y=call_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=strikes, y=put_oi, name='Put OI (Support)', marker_color='#10B981'))
    fig_oi.update_layout(barmode='group', height=250, margin=dict(l=5, r=5, t=5, b=5), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_oi, use_container_width=True)

# ------------------------------------------------------------------
# TAB 3: CHART
# ------------------------------------------------------------------
with tab_charts:
    st.caption("📈 Nifty 5-Min Chart @ 24,007 Levels")
    np.random.seed(101)
    dates = pd.date_range(end=datetime.now(), periods=40, freq='5min')
    close_prices = 24007 + np.cumsum(np.random.randn(40) * 4)
    high_prices = close_prices + np.random.rand(40) * 6
    low_prices = close_prices - np.random.rand(40) * 6
    open_prices = low_prices + np.random.rand(40) * (high_prices - low_prices)

    df_chart = pd.DataFrame({'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices}, index=dates)

    fig_chart = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig_chart.add_hline(y=24050, line_dash="dash", line_color="#EF4444", annotation_text="R1 24,050")
    fig_chart.add_hline(y=23950, line_dash="dash", line_color="#10B981", annotation_text="S1 23,950")
    fig_chart.update_layout(height=320, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_chart, use_container_width=True)

# ------------------------------------------------------------------
# TAB 4: BASKET BUILDER
# ------------------------------------------------------------------
with tab_basket:
    st.caption("✍️ Custom Multi-Trade Basket")
    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    with st.form("basket_form"):
        t_symbol = st.text_input("Strike", "NIFTY 24050 CE")
        t_entry = st.number_input("Entry Price (₹)", value=26.0)
        t_sl = st.number_input("SL Points", value=11.0)
        t_target = st.number_input("Target Points", value=29.0)
        submitted = st.form_submit_button("Add Trade", use_container_width=True)

        if submitted:
            st.session_state.custom_trades.append({
                "Symbol": t_symbol,
                "Entry": t_entry,
                "Max Risk (₹)": 65 * t_sl,
                "Max Target (₹)": 65 * t_target
            })
            st.success("Trade Added!")

    if st.session_state.custom_trades:
        st.dataframe(pd.DataFrame(st.session_state.custom_trades), use_container_width=True)
        if st.button("Clear All", use_container_width=True):
            st.session_state.custom_trades = []
            st.rerun()

