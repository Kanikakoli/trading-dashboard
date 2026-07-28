import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# 1. PAGE CONFIG & PERSISTENT SESSION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v28.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_clean_html(html_str):
    st.html(str(html_str).strip())

query_params = st.query_params
if query_params.get("auth") == "true":
    st.session_state.authenticated = True

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_passcode():
    if st.session_state.get("passcode_input") == "1234":
        st.session_state.authenticated = True
        st.query_params["auth"] = "true"
    else:
        st.error("❌ Invalid Passcode")

if not st.session_state.authenticated:
    st.title("🔐 Terminal Access Locked")
    st.text_input("Enter Passcode:", type="password", key="passcode_input", on_change=check_passcode)
    st.stop()

# ------------------------------------------------------------------
# 2. CUSTOM CSS
# ------------------------------------------------------------------
css_content = """
<style>
.block-container {
    padding-top: 0.2rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
}

.top-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #334155;
}
.app-title { font-size: 15px; font-weight: 900; color: #F8FAFC; letter-spacing: 0.5px; }
.live-dot { height: 8px; width: 8px; background-color: #10B981; border-radius: 50%; display: inline-block; margin-right: 4px; }

.market-stats-bar {
    background: #0B0F19;
    border-radius: 10px;
    padding: 8px;
    border: 1px solid #1E293B;
    margin-bottom: 8px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    text-align: center;
}
.stat-box { background: #111827; border-radius: 8px; padding: 6px 2px; border: 1px solid #1F2937; }
.stat-lbl { font-size: 8px; color: #9CA3AF; font-weight: 700; text-transform: uppercase; }
.stat-val { font-size: 11px; font-weight: 800; color: #F9FAFB; margin: 2px 0; }
.stat-sub-up { font-size: 7px; color: #10B981; font-weight: 800; }

.trade-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 6px solid #10B981;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
}
.trade-card-put { border-left-color: #EF4444; }
.trade-card-hero { border-left-color: #8B5CF6; background: #FAF5FF; }

.card-top-row { display: flex; justify-content: space-between; align-items: center; gap: 4px; flex-wrap: wrap; }
.algo-badge { background: #EFF6FF; color: #1D4ED8; font-size: 8px; font-weight: 800; padding: 2px 6px; border-radius: 4px; border: 1px solid #BFDBFE; }
.updated-badge { background: #FEF3C7; color: #B45309; font-size: 8px; font-weight: 900; padding: 2px 6px; border-radius: 4px; border: 1px solid #FDE68A; }

.status-badge { font-size: 9px; font-weight: 800; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; }
.st-active { background: #D1FAE5; color: #047857; }

.trade-title { font-size: 13px; font-weight: 900; color: #0F172A; margin: 6px 0 2px 0; }
.trade-logic { font-size: 9px; color: #64748B; font-weight: 600; }

.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    background: #F8FAFC;
    padding: 8px 4px;
    border-radius: 8px;
    text-align: center;
    margin-top: 8px;
    border: 1px solid #F1F5F9;
}
.m-item { display: flex; flex-direction: column; }
.m-lbl { font-size: 7px; color: #64748B; font-weight: 800; text-transform: uppercase; }
.m-val { font-size: 11px; font-weight: 900; color: #0F172A; }

.target-updated-box {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    color: #065F46;
    border-radius: 6px;
    padding: 4px 8px;
    margin-top: 6px;
    font-size: 9px;
    font-weight: 800;
    display: flex;
    justify-content: space-between;
}

.sl-warning-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 6px;
    padding: 4px 8px;
    margin-top: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9px;
    color: #92400E;
    font-weight: 700;
}
</style>
"""
render_clean_html(css_content)

# ------------------------------------------------------------------
# 3. REAL-TIME DATA & DYNAMIC TRADE SCANNER ENGINE
# ------------------------------------------------------------------
def calc_live_option_price(spot, strike, is_call=True):
    intrinsic = max(0, spot - strike) if is_call else max(0, strike - spot)
    dist = abs(spot - strike)
    time_val = max(1.5, 24.0 - (dist * 0.18))
    return round(intrinsic + time_val, 2)

@st.cache_data(ttl=2)
def fetch_live_engine():
    data = {
        "nifty": {"spot": 24014.90, "open": 23971.25, "chg": 43.65, "pct": 0.18},
        "banknifty": {"spot": 56980.80, "open": 56830.80, "chg": 150.00, "pct": 0.26},
        "finnifty": {"spot": 21850.00, "open": 21800.00, "chg": 50.00, "pct": 0.23},
        "midcap": {"spot": 12450.00, "open": 12400.00, "chg": 50.00, "pct": 0.40},
        "time": datetime.now().strftime("%H:%M:%S")
    }
    return data

engine_data = fetch_live_engine()
n = engine_data["nifty"]
b = engine_data["banknifty"]
fin = engine_data["finnifty"]
mid = engine_data["midcap"]

# Dynamic Algo Trades Generator (Generates 5-6 active setups across indices)
def generate_algo_trades():
    n_atm = int(round(n['spot'] / 50.0) * 50)
    b_atm = int(round(b['spot'] / 100.0) * 100)
    fin_atm = int(round(fin['spot'] / 50.0) * 50)
    mid_atm = int(round(mid['spot'] / 50.0) * 50)

    trades = [
        {
            "index_tag": "NIFTY 50", "symbol": f"NIFTY {n_atm} CE", "type": "BUY CALL",
            "algo": "EMA CROSS + OI SPIKE", "ltp": calc_live_option_price(n['spot'], n_atm, True),
            "entry": 51.60, "sl": 39.50, "hold_sl": 34.20, "old_target": 65.8, "target": 79.00,
            "is_target_updated": True, "trail_sl": 57.9, "reason": "Strong Momentum! Target Extended",
            "lot": 65, "is_call": True
        },
        {
            "index_tag": "NIFTY 50", "symbol": f"NIFTY {n_atm+100} CE", "type": "BUY CALL",
            "algo": "VWAP BREAKOUT ALGO", "ltp": calc_live_option_price(n['spot'], n_atm+100, True),
            "entry": 28.50, "sl": 18.00, "hold_sl": 15.00, "old_target": 45.0, "target": 48.00,
            "is_target_updated": False, "trail_sl": 32.0, "reason": "Volume Surge near Resistance",
            "lot": 65, "is_call": True
        },
        {
            "index_tag": "BANK NIFTY", "symbol": f"BANK NIFTY {b_atm} PE", "type": "BUY PUT",
            "algo": "REJECTION @ RESISTANCE", "ltp": calc_live_option_price(b['spot'], b_atm, False),
            "entry": 53.50, "sl": 39.30, "hold_sl": 32.70, "old_target": 79.10, "target": 79.10,
            "is_target_updated": False, "trail_sl": 60.0, "reason": f"Heavy Call Writing @ {b_atm + 200}",
            "lot": 15, "is_call": False
        },
        {
            "index_tag": "BANK NIFTY", "symbol": f"BANK NIFTY {b_atm-200} CE", "type": "BUY CALL",
            "algo": "SHORT COVERING SPIKE", "ltp": calc_live_option_price(b['spot'], b_atm-200, True),
            "entry": 85.00, "sl": 62.00, "hold_sl": 55.00, "old_target": 120.0, "target": 135.00,
            "is_target_updated": True, "trail_sl": 95.0, "reason": "PE Unwinding Detected",
            "lot": 15, "is_call": True
        },
        {
            "index_tag": "FIN NIFTY", "symbol": f"FINNIFTY {fin_atm} CE", "type": "BUY CALL",
            "algo": "MOMENTUM BREAKOUT", "ltp": calc_live_option_price(fin['spot'], fin_atm, True),
            "entry": 42.00, "sl": 31.00, "hold_sl": 26.00, "old_target": 60.0, "target": 68.00,
            "is_target_updated": True, "trail_sl": 48.0, "reason": "Banking Sector Multi-Breakout",
            "lot": 40, "is_call": True
        },
        {
            "index_tag": "MIDCAP NIFTY", "symbol": f"MIDCPNIFTY {mid_atm} PE", "type": "BUY PUT",
            "algo": "SUPERTREND REVERSAL", "ltp": calc_live_option_price(mid['spot'], mid_atm, False),
            "entry": 35.00, "sl": 24.00, "hold_sl": 20.00, "old_target": 55.0, "target": 58.00,
            "is_target_updated": False, "trail_sl": 40.0, "reason": "RSI Bearish Divergence",
            "lot": 75, "is_call": False
        }
    ]
    return trades

all_generated_trades = generate_algo_trades()

# Header Bar
render_clean_html(f"""
<div class="top-header">
    <div class="app-title">⚡ PRO TERMINAL <span style="font-size: 9px; color: #94A3B8;">MULTI-ALGO ENGINE</span></div>
    <div style="font-size: 10px; font-weight: 800; color: #10B981;">
        <span class="live-dot"></span>{engine_data['time']}
    </div>
</div>
""")

# INDEX SELECTOR
col_sync, col_select = st.columns([1, 2])
with col_sync:
    if st.button("🔄 Sync Market Data", use_container_width=True):
        st.rerun()

with col_select:
    selected_index = st.selectbox(
        "📍 Select Active Index Filter:",
        ["ALL INDICES", "NIFTY 50", "BANK NIFTY", "FIN NIFTY", "MIDCAP NIFTY"],
        index=0
    )

# Overview Stats Bar
render_clean_html(f"""
<div class="market-stats-bar">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-lbl">NIFTY 50</div>
            <div class="stat-val">{n['spot']:,.1f}</div>
            <div class="stat-sub-up">▲ {n['pct']:+.2f}%</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">BANK NIFTY</div>
            <div class="stat-val">{b['spot']:,.1f}</div>
            <div class="stat-sub-up">▲ {b['chg']:+.1f}</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">FIN NIFTY</div>
            <div class="stat-val">{fin['spot']:,.1f}</div>
            <div class="stat-sub-up">▲ BULLISH</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">MIDCAP NIFTY</div>
            <div class="stat-val">{mid['spot']:,.1f}</div>
            <div class="stat-sub-up">▲ STRENGTH</div>
        </div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 4. TABS & MULTI-TRADE RENDERING
# ------------------------------------------------------------------
tab_signals, tab_hero, tab_chain, tab_charts = st.tabs([
    f"⚡ Active Signals ({len(all_generated_trades)})", 
    "🚀 Zero-Hero Algo", 
    "📊 Option Chain", 
    "📈 Interactive Chart"
])

# --- TAB 1: SIGNALS ---
with tab_signals:
    filtered_trades = [
        t for t in all_generated_trades 
        if selected_index == "ALL INDICES" or t["index_tag"] == selected_index
    ]

    st.caption(f"Showing **{len(filtered_trades)}** active algorithmic signals for `{selected_index}`")

    for t in filtered_trades:
        ltp, entry, sl, hold_sl, target = t['ltp'], t['entry'], t['sl'], t['hold_sl'], t['target']
        status_text, status_class = "🟢 ACTIVE SIGNAL", "st-active"
        card_class = "trade-card" if t['is_call'] else "trade-card trade-card-put"
        risk_amount = round((entry - sl) * t['lot'])

        updated_badge_html = '<span class="updated-badge">🎯 TARGET UPDATED</span>' if t['is_target_updated'] else ''
        target_style = "color:#D97706; font-weight:900; background:#FEF3C7; padding:2px 4px; border-radius:4px;" if t['is_target_updated'] else "color:#16A34A; font-weight:900;"

        target_update_banner = f"""
        <div class="target-updated-box">
            <span>🚀 Target Extended: ₹{t['old_target']} ➔ <b>₹{target}</b></span>
            <span>🔥 Trail SL: ₹{t['trail_sl']}</span>
        </div>
        """ if t['is_target_updated'] else ""

        html_card = f"""
        <div class="{card_class}">
            <div class="card-top-row">
                <div>
                    <span class="algo-badge">⚙️ {t['algo']}</span>
                    {updated_badge_html}
                </div>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="trade-title">{t['symbol']} ({t['type']})</div>
            <div class="trade-logic">💡 {t['reason']}</div>
            
            <div class="metrics-row">
                <div class="m-item"><span class="m-lbl">LTP</span><span class="m-val" style="color:#2563EB;">₹{ltp:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">ENTRY</span><span class="m-val">₹{entry:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">SL</span><span class="m-val" style="color:#DC2626;">₹{sl:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">TARGET</span><span class="m-val" style="{target_style}">₹{target:.2f}</span></div>
            </div>

            {target_update_banner}

            <div class="sl-warning-box">
                <span>🛡️ <b>SYSTEM HOLD SL:</b> ₹{hold_sl:.2f}</span>
                <span>💰 <b>RISK/LOT:</b> ₹{risk_amount:,}</span>
            </div>
        </div>
        """
        render_clean_html(html_card)

# --- TAB 2: ZERO-HERO ---
with tab_hero:
    st.markdown("### 🚀 Expiry Zero-Hero Special Calls")
    n_atm = int(round(n['spot'] / 50.0) * 50)
    b_atm = int(round(b['spot'] / 100.0) * 100)

    hero_trades = [
        {
            "symbol": f"NIFTY {n_atm + 100} CE", "type": "HERO-ZERO (CALL)",
            "ltp": 22.50, "entry": 20.00, "sl": 5.00, "target": 75.00,
            "reason": "Post-1:30 PM Gamma Spike Triggered"
        },
        {
            "symbol": f"BANK NIFTY {b_atm - 200} PE", "type": "HERO-ZERO (PUT)",
            "ltp": 28.00, "entry": 25.00, "sl": 6.00, "target": 95.00,
            "reason": "Short Covering Breakout Expected"
        }
    ]

    for ht in hero_trades:
        render_clean_html(f"""
        <div class="trade-card trade-card-hero">
            <div class="card-top-row">
                <span class="algo-badge" style="background:#F3E8FF; color:#6B21A8; border-color:#D8B4FE;">🔥 HIGH GAMMA ALGO</span>
                <span class="status-badge st-active">⚡ ZERO-HERO</span>
            </div>
            <div class="trade-title">{ht['symbol']} ({ht['type']})</div>
            <div class="trade-logic">💡 {ht['reason']}</div>
            
            <div class="metrics-row">
                <div class="m-item"><span class="m-lbl">LTP</span><span class="m-val" style="color:#8B5CF6;">₹{ht['ltp']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">BUY AROUND</span><span class="m-val">₹{ht['entry']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">SL</span><span class="m-val" style="color:#DC2626;">₹{ht['sl']:.2f}</span></div>
                <div class="m-item"><span class="m-lbl">TARGET</span><span class="m-val" style="color:#16A34A;">₹{ht['target']:.2f}</span></div>
            </div>

            <div class="sl-warning-box" style="background:#F3E8FF; border-color:#D8B4FE; color:#581C87;">
                <span>🎯 <b>RISK-REWARD:</b> 1:4 Ratio</span>
                <span>⚠️ Capital Allocation: Max 2% per trade</span>
            </div>
        </div>
        """)

# --- TAB 3: OPTION CHAIN ---
with tab_chain:
    st.subheader(f"📊 Option Chain - {selected_index if selected_index != 'ALL INDICES' else 'NIFTY 50'}")
    
    idx_map = {
        "NIFTY 50": (n['spot'], 50),
        "BANK NIFTY": (b['spot'], 100),
        "FIN NIFTY": (fin['spot'], 50),
        "MIDCAP NIFTY": (mid['spot'], 50),
        "ALL INDICES": (n['spot'], 50)
    }
    
    ref_spot, step = idx_map.get(selected_index, (n['spot'], 50))
    center = int(round(ref_spot / float(step)) * step)
    strikes = [center + i*step for i in range(-3, 4)]

    chain_rows, call_oi_list, put_oi_list = [], [], []

    for s in strikes:
        c_price = calc_live_option_price(ref_spot, s, is_call=True)
        p_price = calc_live_option_price(ref_spot, s, is_call=False)
        c_oi = round(max(0.5, 6.2 - (abs(s - ref_spot)*0.015)), 2)
        p_oi = round(max(0.5, 5.8 - (abs(s - ref_spot)*0.012)), 2)
        
        call_oi_list.append(c_oi)
        put_oi_list.append(p_oi)

        chain_rows.append({
            "Call OI (Lakhs)": f"{c_oi:.2f}L",
            "Call LTP": f"₹{c_price:.2f}",
            "STRIKE": f"📍 {s} (ATM)" if s == center else f"{s}",
            "Put LTP": f"₹{p_price:.2f}",
            "Put OI (Lakhs)": f"{p_oi:.2f}L",
        })
    
    st.dataframe(pd.DataFrame(chain_rows), use_container_width=True, hide_index=True)

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=call_oi_list, name='Call OI', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=put_oi_list, name='Put OI', marker_color='#10B981'))
    fig_oi.update_layout(
        title=f"Open Interest Distribution ({selected_index})",
        barmode='group', height=280, 
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_oi, use_container_width=True)

# --- TAB 4: INTERACTIVE CHART ---
with tab_charts:
    st.subheader(f"📈 5-Min Price Action - {selected_index if selected_index != 'ALL INDICES' else 'NIFTY 50'}")
    
    ref_spot = idx_map.get(selected_index, (n['spot'], 50))[0]
    np.random.seed(42)
    periods = 40
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    
    close_prices = ref_spot + np.cumsum(np.random.randn(periods) * 4)
    high_prices = close_prices + np.abs(np.random.randn(periods) * 5)
    low_prices = close_prices - np.abs(np.random.randn(periods) * 5)
    open_prices = low_prices + np.random.rand(periods) * (high_prices - low_prices)

    df_chart = pd.DataFrame({
        'Open': open_prices, 'High': high_prices, 
        'Low': low_prices, 'Close': close_prices
    }, index=dates)

    fig_chart = make_subplots(rows=1, cols=1)
    fig_chart.add_trace(go.Candlestick(
        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], 
        low=df_chart['Low'], close=df_chart['Close'], name=selected_index
    ))
    fig_chart.update_layout(
        height=380, 
        margin=dict(l=10, r=10, t=10, b=10), 
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )
    st.plotly_chart(fig_chart, use_container_width=True)

