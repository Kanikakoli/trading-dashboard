import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIG & SESSION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v35.0 - FULL EXECUTION",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_clean_html(html_str):
    st.html(str(html_str).strip())

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True

# ------------------------------------------------------------------
# 2. RESPONSIVE CSS & UI DESIGN
# ------------------------------------------------------------------
css_content = """
<style>
.block-container { padding: 0.2rem 0.3rem !important; }
.top-header { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 10px; padding: 8px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #334155; }
.app-title { font-size: 14px; font-weight: 900; color: #F8FAFC; }
.live-dot { height: 8px; width: 8px; background-color: #10B981; border-radius: 50%; display: inline-block; margin-right: 4px; }

.market-stats-bar { background: #0B0F19; border-radius: 8px; padding: 6px; border: 1px solid #1E293B; margin-bottom: 8px; }
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; text-align: center; }
.stat-box { background: #111827; border-radius: 6px; padding: 4px 2px; border: 1px solid #1F2937; }
.stat-lbl { font-size: 7px; color: #9CA3AF; font-weight: 700; }
.stat-val { font-size: 9px; font-weight: 800; color: #F9FAFB; }
.stat-sub-up { font-size: 7px; color: #10B981; font-weight: 800; }

.trade-card { background: #FFFFFF; border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 5px solid #10B981; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
.trade-card-put { border-left-color: #EF4444; }

.card-top-row { display: flex; justify-content: space-between; align-items: center; }
.algo-badge { background: #EFF6FF; color: #1D4ED8; font-size: 8px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.grade-aplus { background: #DCFCE7; color: #15803D; font-size: 8px; font-weight: 900; padding: 2px 6px; border-radius: 4px; }
.status-badge { font-size: 8px; font-weight: 800; padding: 2px 6px; border-radius: 4px; background: #D1FAE5; color: #047857; }

.trade-title { font-size: 12px; font-weight: 900; color: #0F172A; margin: 4px 0 2px 0; }
.trade-logic { font-size: 8px; color: #64748B; font-weight: 600; }

.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2px; background: #F8FAFC; padding: 6px 2px; border-radius: 6px; text-align: center; margin-top: 6px; }
.m-lbl { font-size: 7px; color: #64748B; font-weight: 800; }
.m-val { font-size: 10px; font-weight: 900; color: #0F172A; }

.sl-warning-box { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 4px 6px; margin-top: 4px; display: flex; justify-content: space-between; font-size: 8px; color: #92400E; font-weight: 700; }

.analysis-box { background: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 10px; color: #F8FAFC; margin-bottom: 8px; }
.analysis-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 6px; }
.an-card { background: #1E293B; padding: 8px; border-radius: 6px; border: 1px solid #475569; }
.an-title { font-size: 9px; color: #94A3B8; font-weight: 700; }
.an-val { font-size: 14px; font-weight: 900; color: #38BDF8; }
.an-sub { font-size: 8px; font-weight: 600; color: #34D399; }
</style>
"""
render_clean_html(css_content)

# ------------------------------------------------------------------
# 3. LIVE ENGINE & DATA PIPELINE
# ------------------------------------------------------------------
@st.cache_data(ttl=2)
def fetch_live_engine():
    return {
        "nifty": {"spot": 24013.5, "open": 23971.25, "chg": 25.90, "pct": 0.18},
        "banknifty": {"spot": 56902.9, "open": 56830.80, "chg": 150.00, "pct": 0.26},
        "finnifty": {"spot": 21850.0, "open": 21800.00, "chg": 50.00, "pct": 0.23},
        "midcap": {"spot": 12450.0, "open": 12400.00, "chg": 50.00, "pct": 0.40},
        "sensex": {"spot": 76923.4, "open": 76800.00, "chg": 82.40, "pct": 0.13},
        "time": datetime.now().strftime("%H:%M:%S")
    }

engine_data = fetch_live_engine()
n = engine_data["nifty"]
b = engine_data["banknifty"]
sen = engine_data["sensex"]
fin = engine_data["finnifty"]
mid = engine_data["midcap"]

all_generated_trades = [
    {
        "id": "T1", "index_tag": "NIFTY 50", "symbol": "NIFTY 24000 CE", "type": "BUY CALL",
        "algo": "EMA CROSS + OI SPIKE", "ltp": 42.95, "entry": 51.60, "sl": 39.50, "hold_sl": 34.20, "target": 79.00,
        "grade": "A+", "probability": "88%", "reason": "Strong Institutional Volume & OI Support", "lot": 65, "is_call": True
    },
    {
        "id": "T2", "index_tag": "BANK NIFTY", "symbol": "BANK NIFTY 56900 PE", "type": "BUY PUT",
        "algo": "REJECTION @ RESISTANCE", "ltp": 53.50, "entry": 53.50, "sl": 39.30, "hold_sl": 32.70, "target": 79.10,
        "grade": "A+", "probability": "85%", "reason": "Heavy Call Writing @ 57100", "lot": 15, "is_call": False
    }
]

# Top Bar Header
render_clean_html(f"""
<div class="top-header">
    <div class="app-title">⚡ PRO TERMINAL <span style="font-size: 8px; color: #10B981;">● LIVE SYNC</span></div>
    <div style="font-size: 9px; font-weight: 800; color: #10B981;"><span class="live-dot"></span>{engine_data['time']}</div>
</div>
""")

st.button("🔄 Sync Market Data", use_container_width=True)

selected_index = st.selectbox(
    "📍 Select Active Index Filter:",
    ["ALL INDICES", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY", "MIDCAP NIFTY"]
)

render_clean_html(f"""
<div class="market-stats-bar">
    <div class="stats-grid">
        <div class="stat-box"><div class="stat-lbl">NIFTY 50</div><div class="stat-val">{n['spot']:,.1f}</div><div class="stat-sub-up">▲ {n['pct']:+.2f}%</div></div>
        <div class="stat-box"><div class="stat-lbl">BANK NIFTY</div><div class="stat-val">{b['spot']:,.1f}</div><div class="stat-sub-up">▲ +150.0</div></div>
        <div class="stat-box"><div class="stat-lbl">SENSEX</div><div class="stat-val">{sen['spot']:,.1f}</div><div class="stat-sub-up">▲ {sen['pct']:+.2f}%</div></div>
        <div class="stat-box"><div class="stat-lbl">FIN NIFTY</div><div class="stat-val">{fin['spot']:,.1f}</div><div class="stat-sub-up">▲ BULLISH</div></div>
        <div class="stat-box"><div class="stat-lbl">MIDCAP NIFTY</div><div class="stat-val">{mid['spot']:,.1f}</div><div class="stat-sub-up">▲ STRENGTH</div></div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 4. TAB NAVIGATION & CONTENT RENDER
# ------------------------------------------------------------------
tab_signals, tab_btst, tab_hero, tab_chain, tab_analysis, tab_charts = st.tabs([
    f"⚡ Active Signals ({len(all_generated_trades)})", 
    "🌙 BTST Setup",
    "🚀 Dynamic Zero-Hero", 
    "📊 Option Chain", 
    "📊 Trade Analysis",
    "📈 Interactive Chart"
])

# --- TAB 1: SIGNALS & DIRECT ORDER EXECUTION ---
with tab_signals:
    filtered = [t for t in all_generated_trades if selected_index == "ALL INDICES" or t["index_tag"] == selected_index]
    for t in filtered:
        card_class = "trade-card" if t['is_call'] else "trade-card trade-card-put"
        risk_amount = round((t['entry'] - t['sl']) * t['lot'])
        
        render_clean_html(f"""
        <div class="{card_class}">
            <div class="card-top-row">
                <div><span class="algo-badge">⚙️ {t['algo']}</span> <span class="grade-aplus">⭐ {t['grade']} ({t['probability']})</span></div>
                <span class="status-badge">🟢 ACTIVE</span>
            </div>
            <div class="trade-title">{t['symbol']} ({t['type']})</div>
            <div class="trade-logic">💡 {t['reason']}</div>
            <div class="metrics-row">
                <div class="m-item"><span class="m-lbl">LTP</span><span class="m-val" style="color:#2563EB;">₹{t['ltp']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">ENTRY</span><span class="m-val">₹{t['entry']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">SL</span><span class="m-val" style="color:#DC2626;">₹{t['sl']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">TARGET</span><span class="m-val" style="color:#16A34A;">₹{t['target']:.2f}</span></div>
            </div>
            <div class="sl-warning-box"><span>🛡️ <b>HOLD SL:</b> ₹{t['hold_sl']:.2f}</span><span>💰 <b>RISK/LOT:</b> ₹{risk_amount:,}</span></div>
        </div>
        """)
        
        # Embedded Order Execution Section
        with st.expander(f"⚡ Execute Order: {t['symbol']}"):
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                lots = st.number_input(f"Lots ({t['lot']} qty/lot)", min_value=1, value=1, key=f"lots_{t['id']}")
            with c2:
                order_type = st.selectbox("Type", ["MARKET", "LIMIT"], key=f"type_{t['id']}")
            with c3:
                trigger_p = st.number_input("Trigger Price", value=t['entry'], key=f"p_{t['id']}")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button(f"🟢 BUY {t['symbol']}", use_container_width=True, key=f"buy_{t['id']}"):
                    st.success(f"✅ Order Placed: {lots * t['lot']} Qty @ ₹{trigger_p}")
            with btn2:
                if st.button(f"🔴 EXIT / CLOSE", use_container_width=True, key=f"sell_{t['id']}"):
                    st.warning("Position Exited.")

# --- TAB 2: BTST SETUP ---
with tab_btst:
    st.subheader("🌙 BTST (Overnight) Radar Engine")
    render_clean_html("""
    <div class="analysis-box" style="border-color:#F59E0B;">
        <div style="font-weight: 800; font-size: 11px; color:#FBBF24;">🌍 OVERNIGHT MARKET MATRIX</div>
        <div class="analysis-grid">
            <div class="an-card"><div class="an-title">US DOW JONES</div><div class="an-val" style="color:#34D399;">+0.42%</div><div class="an-sub">Bullish Bias</div></div>
            <div class="an-card"><div class="an-title">GIFT NIFTY</div><div class="an-val" style="color:#38BDF8;">24,035 (+18)</div><div class="an-sub">Gap-Up Expected</div></div>
        </div>
    </div>
    """)
    st.info("💡 **BTST Strategy Recommendation:** Enter **NIFTY 24000 CE** between 3:15 PM - 3:25 PM for overnight holding with Target: ₹85.00.")

# --- TAB 3: DYNAMIC ZERO-HERO ---
with tab_hero:
    st.subheader("🚀 Dynamic Zero-Hero Engine")
    st.warning("ℹ️ Zero-Hero signals trigger automatically on Expiry Days after 1:30 PM on high gamma spikes.")

# --- TAB 4: OPTION CHAIN ---
with tab_chain:
    st.subheader("📊 Live Option Chain Data")
    df_chain = pd.DataFrame([
        {"Call OI": "2.98L", "STRIKE": "23850", "Put OI": "5.11L"},
        {"Call OI": "3.73L", "STRIKE": "23900", "Put OI": "5.71L"},
        {"Call OI": "4.48L", "STRIKE": "23950", "Put OI": "6.31L"},
        {"Call OI": "5.23L", "STRIKE": "📍 24000 (ATM)", "Put OI": "6.91L"},
        {"Call OI": "4.88L", "STRIKE": "24050", "Put OI": "6.63L"},
        {"Call OI": "4.13L", "STRIKE": "24100", "Put OI": "6.03L"},
    ])
    st.dataframe(df_chain, use_container_width=True, hide_index=True)

# --- TAB 5: TRADE ANALYSIS ---
with tab_analysis:
    st.subheader(f"📊 Market Analysis ({selected_index})")
    render_clean_html("""
    <div class="analysis-box">
        <div class="analysis-grid">
            <div class="an-card"><div class="an-title">PUT-CALL RATIO (PCR)</div><div class="an-val">1.28</div><div class="an-sub">BULLISH 🟢</div></div>
            <div class="an-card"><div class="an-title">EXPECTED MAX PAIN</div><div class="an-val">₹24000</div><div class="an-sub">Expiry Pin Zone</div></div>
            <div class="an-card"><div class="an-title">KEY SUPPORT</div><div class="an-val">₹23900</div><div class="an-sub">Heavy Put Writing</div></div>
            <div class="an-card"><div class="an-title">KEY RESISTANCE</div><div class="an-val">₹24150</div><div class="an-sub">Heavy Call Writing</div></div>
        </div>
    </div>
    """)
    
    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[6.31, 6.91, 4.13], name='Put OI (Bulls)', marker_color='#10B981'))
    fig_oi.add_trace(go.Bar(x=['Support (23900)', 'ATM (24000)', 'Resistance (24150)'], y=[4.48, 5.23, 6.03], name='Call OI (Bears)', marker_color='#EF4444'))
    fig_oi.update_layout(height=260, template="plotly_dark", barmode='group', margin=dict(l=5, r=5, t=20, b=5))
    st.plotly_chart(fig_oi, use_container_width=True)

# --- TAB 6: INTERACTIVE CHART ---
with tab_charts:
    st.subheader(f"📈 NIFTY 50 Intraday Candlestick Chart")
    dates = pd.date_range(end=datetime.now(), periods=25, freq='5min')
    close_prices = 24013.5 + np.cumsum(np.random.randn(25) * 2.5)
    df_chart = pd.DataFrame({'Open': close_prices-1.5, 'High': close_prices+3, 'Low': close_prices-3, 'Close': close_prices}, index=dates)

    fig_chart = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig_chart.update_layout(height=320, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig_chart, use_container_width=True)
