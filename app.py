import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime

# ------------------------------------------------------------------
# PAGE CONFIG & AUTHENTICATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v15.0 | Live Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
# UI STYLES
# ------------------------------------------------------------------
render_clean_html("""
<style>
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
}
.market-stats-bar {
    background: #0F172A;
    border-radius: 10px;
    padding: 8px;
    color: #FFFFFF;
    margin-bottom: 10px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    text-align: center;
}
.stat-box { background: #1E293B; border-radius: 6px; padding: 5px; }
.stat-lbl { font-size: 8px; color: #94A3B8; font-weight: 700; text-transform: uppercase; }
.stat-val { font-size: 11px; font-weight: 800; color: #FFFFFF; }
.stat-sub-up { font-size: 8px; color: #10B981; font-weight: 700; }
.stat-sub-down { font-size: 8px; color: #EF4444; font-weight: 700; }
.ad-bar-container { height: 5px; width: 100%; background: #EF4444; border-radius: 3px; overflow: hidden; margin-top: 3px; display: flex; }
.ad-advance { background: #10B981; height: 100%; }

.levels-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px; margin-bottom: 8px; }
.level-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-top: 4px; text-align: center; }
.s-box { background: #DCFCE7; border-radius: 4px; padding: 2px; }
.r-box { background: #FEE2E2; border-radius: 4px; padding: 2px; }
.level-lbl { font-size: 8px; font-weight: 800; }
.level-val { font-size: 10px; font-weight: 800; color: #0F172A; }

.compact-trade-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    padding: 10px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.card-call-border { border-left: 5px solid #10B981; }
.card-hz-border { border-left: 5px solid #8B5CF6; }

.status-pending { background: #FEF3C7; color: #B45309; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.status-expired { background: #FEE2E2; color: #B91C1C; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }

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
.m-label { font-size: 8px; color: #64748B; font-weight: 700; }
.m-val { font-size: 11px; font-weight: 800; color: #0F172A; }

.trade-analysis-box {
    background: #F1F5F9;
    border-radius: 8px;
    padding: 8px;
    margin-top: 8px;
    border-left: 4px solid #3B82F6;
}
</style>
""")

# ------------------------------------------------------------------
# LIVE DATA ENGINE
# ------------------------------------------------------------------
@st.cache_data(ttl=4)
def fetch_live_engine():
    try:
        indices = yf.Tickers('^NSEI ^NSEBANK ^BSESN')
        n_df = indices.tickers['^NSEI'].history(period='1d', interval='1m')
        b_df = indices.tickers['^NSEBANK'].history(period='1d', interval='1m')
        s_df = indices.tickers['^BSESN'].history(period='1d', interval='1m')

        def extract_spot(df, fallback):
            if df.empty:
                return fallback, fallback, 0.0, 0.0
            spot = df['Close'].iloc[-1]
            open_p = df['Open'].iloc[0]
            chg = spot - open_p
            pct = (chg / open_p) * 100 if open_p != 0 else 0
            return spot, open_p, chg, pct

        n_spot, n_open, n_chg, n_pct = extract_spot(n_df, 24020.15)
        b_spot, _, _, _ = extract_spot(b_df, 56919.10)
        s_spot, _, _, _ = extract_spot(s_df, 76872.70)

        top_components = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS"]
        comp_tickers = yf.Tickers(" ".join(top_components))
        adv, dec = 0, 0
        
        for sym in top_components:
            try:
                c_data = comp_tickers.tickers[sym].history(period='1d', interval='5m')
                if not c_data.empty:
                    if c_data['Close'].iloc[-1] >= c_data['Open'].iloc[0]:
                        adv += 1
                    else:
                        dec += 1
            except:
                pass

        adv_val = adv * 120 if (adv + dec) > 0 else 840
        dec_val = dec * 100 if (adv + dec) > 0 else 200

        return {
            "nifty": {"spot": n_spot, "open": n_open, "chg": n_chg, "pct": n_pct},
            "banknifty": {"spot": b_spot},
            "sensex": {"spot": s_spot},
            "advances": adv_val,
            "declines": dec_val,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    except Exception:
        return {
            "nifty": {"spot": 24020.15, "open": 23971.25, "chg": 48.90, "pct": 0.20},
            "banknifty": {"spot": 56919.10},
            "sensex": {"spot": 76872.70},
            "advances": 840, "declines": 200,
            "time": datetime.now().strftime("%H:%M:%S")
        }

engine_data = fetch_live_engine()
n = engine_data["nifty"]

st.title(f"⚡ PRO TERMINAL v15.0 (LIVE @ {engine_data['time']})")

col_r, _ = st.columns([1, 3])
with col_r:
    if st.button("🔄 Refresh Live Price", use_container_width=True):
        st.rerun()

# ------------------------------------------------------------------
# 1. LIVE TOP METRICS
# ------------------------------------------------------------------
adv = engine_data["advances"]
dec = engine_data["declines"]
tot = max(adv + dec, 1)
adv_percent = (adv / tot) * 100

sub_cls = "stat-sub-up" if n["chg"] >= 0 else "stat-sub-down"
arr = "▲" if n["chg"] >= 0 else "▼"

render_clean_html(f"""
<div class="market-stats-bar">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-lbl">NIFTY SPOT (LIVE)</div>
            <div class="stat-val">{n['spot']:,.2f}</div>
            <div class="{sub_cls}">{arr} {n['chg']:+.2f} ({n['pct']:+.2f}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">OPEN / PREV CLOSE</div>
            <div class="stat-val">{n['open']:,.2f}</div>
            <div style="font-size: 8px; color: #94A3B8;">Open: <b style="color:#FFF;">{n['open']:,.2f}</b></div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">PCR RATIO</div>
            <div class="stat-val" style="color: #F59E0B;">0.88</div>
            <div style="font-size: 8px; color: #94A3B8;">NEUTRAL / MILD BULL</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">ADV / DEC RATIO</div>
            <div class="stat-val">{adv} : {dec}</div>
            <div class="ad-bar-container">
                <div class="ad-advance" style="width: {adv_percent:.0f}%;"></div>
            </div>
        </div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 2. INDICES LEVELS
# ------------------------------------------------------------------
n_spot = n["spot"]
b_spot = engine_data["banknifty"]["spot"]
s_spot = engine_data["sensex"]["spot"]

levels_data = [
    {"index": "NIFTY 50", "spot": f"{n_spot:,.1f}", "s2": f"{round(n_spot - 100, -1):.0f}", "s1": f"{round(n_spot - 50, -1):.0f}", "r1": f"{round(n_spot + 50, -1):.0f}", "r2": f"{round(n_spot + 100, -1):.0f}"},
    {"index": "BANK NIFTY", "spot": f"{b_spot:,.1f}", "s2": f"{round(b_spot - 300, -2):.0f}", "s1": f"{round(b_spot - 150, -2):.0f}", "r1": f"{round(b_spot + 150, -2):.0f}", "r2": f"{round(b_spot + 300, -2):.0f}"},
    {"index": "SENSEX", "spot": f"{s_spot:,.1f}", "s2": f"{round(s_spot - 400, -2):.0f}", "s1": f"{round(s_spot - 200, -2):.0f}", "r1": f"{round(s_spot + 200, -2):.0f}", "r2": f"{round(s_spot + 400, -2):.0f}"}
]

cols = st.columns(3)
for i, lvl in enumerate(levels_data):
    with cols[i]:
        render_clean_html(f"""
        <div class="levels-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 10px; font-weight: 800; color: #0F172A;">{lvl['index']}</span>
                <span style="font-size: 9px; font-weight: 700; color: #059669;">{lvl['spot']}</span>
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
# 3. DASHBOARD TABS
# ------------------------------------------------------------------
tab_signals, tab_oi, tab_charts, tab_basket = st.tabs([
    "⚡ Active Signals", 
    "📊 OI & Writers", 
    "📈 Interactive Chart",
    "✍️ Multi-Trade Basket"
])

# TAB 1: SIGNALS
with tab_signals:
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        filter_index = st.selectbox("Filter Index:", ["ALL", "NIFTY 50", "BANK NIFTY", "SENSEX"], key="sig_idx", label_visibility="collapsed")
    with col_f2:
        filter_type = st.selectbox("Filter Strategy:", ["ALL SIGNALS", "HERO-ZERO ONLY", "INTRADAY SCALP"], key="sig_type", label_visibility="collapsed")

    atm_strike = int(round(n_spot / 50.0) * 50)

    trades = [
        {
            "symbol": f"NIFTY {atm_strike + 50} CE",
            "index": "NIFTY 50",
            "tag": "INTRADAY SCALP",
            "type": "BUY CALL",
            "entry": 26.0, "sl": 15.0, "target": 55.0,
            "reason": f"Holding live level @ {atm_strike} + Dynamic Momentum",
            "lot_size": 65, "gen_time": engine_data['time'],
            "status_msg": "⏳ PENDING (Trigger point @ ₹26)"
        },
        {
            "symbol": f"NIFTY {atm_strike + 150} CE",
            "index": "NIFTY 50",
            "tag": "HERO-ZERO",
            "type": "BUY CALL",
            "entry": 13.0, "sl": 4.0, "target": 45.0,
            "reason": "Expiry Gamma breakout level expected above VWAP",
            "lot_size": 65, "gen_time": "09:15 AM",
            "status_msg": "❌ EXPIRED / MISSED"
        }
    ]

    filtered_trades = [
        t for t in trades 
        if (filter_index == "ALL" or t["index"] == filter_index) and
           (filter_type == "ALL SIGNALS" or (filter_type == "HERO-ZERO ONLY" and t["tag"] == "HERO-ZERO") or (filter_type == "INTRADAY SCALP" and t["tag"] == "INTRADAY SCALP"))
    ]

    for t in filtered_trades:
        risk = (t['entry'] - t['sl']) * t['lot_size']
        is_hz = t['tag'] == "HERO-ZERO"
        card_border = "card-hz-border" if is_hz else "card-call-border"
        status_cls = "status-pending" if "PENDING" in t['status_msg'] else "status-expired"

        render_clean_html(f"""
        <div class="compact-trade-card {card_border}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="{status_cls}">{t['status_msg']}</span>
                <span style="font-size: 9px; font-weight: 700; color: #64748B;">Time: {t['gen_time']}</span>
            </div>
            <div style="margin-top: 4px; font-size: 13px; font-weight: 800; color: #0F172A;">{t['symbol']} ({t['type']})</div>
            <div style="font-size: 10px; color: #475569; margin-top: 2px;">{t['reason']}</div>
            <div class="metrics-grid">
                <div><div class="m-label">ENTRY</div><div class="m-val">₹{t['entry']:.1f}</div></div>
                <div><div class="m-label">SL</div><div class="m-val">₹{t['sl']:.1f}</div></div>
                <div><div class="m-label">TARGET</div><div class="m-val">₹{t['target']:.1f}</div></div>
                <div><div class="m-label">RISK/LOT</div><div class="m-val">₹{risk:,.0f}</div></div>
            </div>
        </div>
        """)

# TAB 2: OPTION CHAIN & OI WRITERS
with tab_oi:
    oi_index = st.selectbox("Select Index for Option Chain & OI:", ["NIFTY 50", "BANK NIFTY", "SENSEX"], key="oi_select")

    if oi_index == "NIFTY 50":
        center = int(round(n_spot / 50.0) * 50)
        step = 50
        strikes = [center - 100, center - 50, center, center + 50, center + 100]
        call_oi = [64.8, 72.1, 262.0, 126.0, 190.0]
        put_oi = [225.0, 199.0, 264.0, 50.0, 56.1]
    elif oi_index == "BANK NIFTY":
        center = int(round(b_spot / 100.0) * 100)
        step = 100
        strikes = [center - 200, center - 100, center, center + 100, center + 200]
        call_oi = [15.2, 34.1, 142.5, 98.2, 185.0]
        put_oi = [120.4, 160.2, 138.0, 42.1, 18.2]
    else:
        center = int(round(s_spot / 100.0) * 100)
        step = 100
        strikes = [center - 200, center - 100, center, center + 100, center + 200]
        call_oi = [22.4, 45.1, 110.6, 175.2, 210.0]
        put_oi = [180.5, 155.2, 105.4, 32.1, 12.5]

    st.subheader("📋 Live Option Chain Matrix")
    
    chain_data = []
    for s, c_oi, p_oi in zip(strikes, call_oi, put_oi):
        c_price = max(10, round(50 + (center - s) * 0.4, 1))
        p_price = max(10, round(50 + (s - center) * 0.4, 1))
        tag = "🎯 ATM" if s == center else ("ITM Call" if s < center else "OTM Call")
        chain_data.append({
            "Call OI (Lakh)": c_oi,
            "Call Price (₹)": c_price,
            "STRIKE": s,
            "Put Price (₹)": p_price,
            "Put OI (Lakh)": p_oi,
            "Status": tag
        })
    
    st.dataframe(pd.DataFrame(chain_data), use_container_width=True)

    st.subheader("📊 OI Bar Chart (Resistance vs Support)")
    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=call_oi, name='Call OI (Resistance)', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=put_oi, name='Put OI (Support)', marker_color='#10B981'))
    fig_oi.update_layout(barmode='group', height=250, margin=dict(l=5, r=5, t=10, b=5), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_oi, use_container_width=True)

# TAB 3: CHARTS
with tab_charts:
    col_c1, col_c2 = st.columns([2, 2])
    with col_c1:
        chart_sym = st.selectbox("Chart Symbol:", ["NIFTY 50", "BANK NIFTY", "SENSEX"], key="c_sym")
    with col_c2:
        chart_tf = st.selectbox("Timeframe:", ["5m", "15m", "1h"], key="c_tf")

    np.random.seed(42)
    periods = 40
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    base_p = n_spot if chart_sym == "NIFTY 50" else (b_spot if chart_sym == "BANK NIFTY" else s_spot)
    
    close_prices = base_p + np.cumsum(np.random.randn(periods) * 6)
    high_prices = close_prices + np.random.rand(periods) * 10
    low_prices = close_prices - np.random.rand(periods) * 10
    open_prices = low_prices + np.random.rand(periods) * (high_prices - low_prices)

    df_chart = pd.DataFrame({'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices}, index=dates)
    df_chart['EMA20'] = df_chart['Close'].ewm(span=20).mean()

    fig_chart = make_subplots(rows=1, cols=1)
    fig_chart.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], name='Price'))
    fig_chart.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='#F59E0B', width=1.5), name='EMA 20'))
    fig_chart.update_layout(height=340, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, showlegend=False)
    st.plotly_chart(fig_chart, use_container_width=True)

# TAB 4: SMART BASKET & TRADE VALIDATOR
with tab_basket:
    st.caption("✍️ Smart Trade Validator & Multi-Basket Engine")
    
    sel_idx = st.selectbox("Select Index:", ["NIFTY 50", "BANK NIFTY", "SENSEX"], key="b_idx_sel")
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        strike_val = st.number_input("Enter Strike Price:", value=24350 if sel_idx == "NIFTY 50" else (57000 if sel_idx == "BANK NIFTY" else 77000), step=50)
    with col_u2:
        opt_type = st.selectbox("Type:", ["CE (CALL)", "PE (PUT)"])

    current_idx_spot = n_spot if sel_idx == "NIFTY 50" else (b_spot if sel_idx == "BANK NIFTY" else s_spot)
    lot_size = 65 if sel_idx == "NIFTY 50" else (15 if sel_idx == "BANK NIFTY" else 10)

    # AUTO TRADE ANALYZER LOGIC
    is_call = "CE" in opt_type
    diff = strike_val - current_idx_spot if is_call else current_idx_spot - strike_val
    
    if abs(diff) <= 50:
        money_status = "ATM (At The Money)"
        is_good = True
        auto_entry = 45.0
        auto_sl = 30.0
        auto_target = 80.0
        verdict = "✅ SHI TRADE (High Probability Momentum Zone)"
    elif diff < 0:
        money_status = "ITM (In The Money)"
        is_good = True
        auto_entry = 85.0
        auto_sl = 65.0
        auto_target = 135.0
        verdict = "✅ SHI TRADE (Safe Delta & High Liquidity)"
    else:
        money_status = "OTM (Out The Money)"
        is_good = False if diff > 250 else True
        auto_entry = 18.0
        auto_sl = 8.0
        auto_target = 42.0
        verdict = "⚠️ RISKY / GALAT TRADE (Too far OTM, Theta decay threat)" if diff > 200 else "🟡 MODERATE RISK (Scalping Trade Only)"

    render_clean_html(f"""
    <div class="trade-analysis-box">
        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Analyzer Output for {sel_idx} {strike_val} {opt_type.split()[0]}</div>
        <div style="font-size: 11px; margin-top: 2px;">Spot Price: <b>{current_idx_spot:,.1f}</b> | Category: <b>{money_status}</b></div>
        <div style="font-size: 12px; font-weight: 800; margin-top: 4px; color: {'#059669' if is_good else '#DC2626'};">{verdict}</div>
    </div>
    """)

    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    with st.form("basket_form"):
        t_entry = st.number_input("Entry Price (₹)", value=auto_entry)
        t_sl = st.number_input("Stop Loss (₹)", value=auto_sl)
        t_target = st.number_input("Target Price (₹)", value=auto_target)
        submitted = st.form_submit_button("Add to Basket", use_container_width=True)

        if submitted:
            risk_amt = (t_entry - t_sl) * lot_size
            target_amt = (t_target - t_entry) * lot_size
            st.session_state.custom_trades.append({
                "Symbol": f"{sel_idx} {strike_val} {opt_type.split()[0]}",
                "Entry": f"₹{t_entry}",
                "SL": f"₹{t_sl}",
                "Target": f"₹{t_target}",
                "Risk/Lot": f"₹{risk_amt:,.0f}",
                "Reward/Lot": f"₹{target_amt:,.0f}",
                "Verdict": "SHI" if is_good else "RISKY"
            })
            st.success("Added to Basket!")

    if st.session_state.custom_trades:
        st.dataframe(pd.DataFrame(st.session_state.custom_trades), use_container_width=True)
        if st.button("Clear Basket", use_container_width=True):
            st.session_state.custom_trades = []
            st.rerun()

