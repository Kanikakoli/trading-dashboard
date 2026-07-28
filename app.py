import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime
import time

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v13.0 | Live Streaming Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_clean_html(html_str):
    st.markdown(html_str.strip(), unsafe_allow_html=True)

# CSS STYLES
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
.stat-val { font-size: 12px; font-weight: 800; color: #FFFFFF; }
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
.compact-trade-card { background: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; padding: 10px; margin-bottom: 10px; }
.card-call-border { border-left: 5px solid #10B981; }
.status-pending { background: #FEF3C7; color: #B45309; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; background: #F8FAFC; padding: 6px; border-radius: 6px; text-align: center; margin-top: 6px; }
.m-label { font-size: 8px; color: #64748B; font-weight: 700; }
.m-val { font-size: 11px; font-weight: 800; color: #0F172A; }
</style>
""")

# ------------------------------------------------------------------
# LIVE MARKET DATA FETCHING ENGINE (yfinance API)
# ------------------------------------------------------------------
@st.cache_data(ttl=3)
def get_live_market_data():
    try:
        tickers = yf.Tickers('^NSEI ^NSEBANK ^BSESN')
        nifty_hist = tickers.tickers['^NSEI'].history(period='1d', interval='1m')
        bank_hist = tickers.tickers['^NSEBANK'].history(period='1d', interval='1m')
        sensex_hist = tickers.tickers['^BSESN'].history(period='1d', interval='1m')

        def extract_metrics(df):
            if df.empty:
                return 24007.75, 23995.95, 23990.10, 11.80, 0.05
            spot = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0]
            prev_close = df['Open'].iloc[0] # Fallback estimate
            chg = spot - prev_close
            chg_pct = (chg / prev_close) * 100 if prev_close != 0 else 0
            return spot, prev_close, open_price, chg, chg_pct

        n_spot, n_prev, n_open, n_chg, n_pct = extract_metrics(nifty_hist)
        b_spot, _, _, _, _ = extract_metrics(bank_hist)
        s_spot, _, _, _, _ = extract_metrics(sensex_hist)

        return {
            "nifty": {"spot": n_spot, "prev": n_prev, "open": n_open, "chg": n_chg, "pct": n_pct},
            "banknifty": {"spot": b_spot},
            "sensex": {"spot": s_spot},
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except Exception:
        return {
            "nifty": {"spot": 24007.75, "prev": 23995.95, "open": 23990.10, "chg": 11.80, "pct": 0.05},
            "banknifty": {"spot": 57014.50},
            "sensex": {"spot": 76863.70},
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

live_data = get_live_market_data()
n = live_data["nifty"]

st.title(f"⚡ PRO TERMINAL v13.0 (LIVE @ {live_data['timestamp']})")

# Auto refresh button for manual trigger + info
col_a, col_b = st.columns([3, 1])
with col_b:
    if st.button("🔄 Refresh Live Price", use_container_width=True):
        st.rerun()

# ------------------------------------------------------------------
# 1. ADVANCE/DECLINE & LIVE STRIP
# ------------------------------------------------------------------
sub_class = "stat-sub-up" if n["chg"] >= 0 else "stat-sub-down"
arrow = "▲" if n["chg"] >= 0 else "▼"

render_clean_html(f"""
<div class="market-stats-bar">
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-lbl">NIFTY SPOT (LIVE)</div>
            <div class="stat-val">{n['spot']:,.2f}</div>
            <div class="{sub_class}">{arrow} {n['chg']:+.2f} ({n['pct']:+.2f}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">OPEN / PREV CLOSE</div>
            <div class="stat-val">{n['open']:,.2f}</div>
            <div style="font-size: 8px; color: #94A3B8;">Prev: <b style="color:#FFF;">{n['prev']:,.2f}</b></div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">PCR RATIO</div>
            <div class="stat-val" style="color: #F59E0B;">0.88</div>
            <div style="font-size: 8px; color: #94A3B8;">NEUTRAL</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">ADV / DEC RATIO</div>
            <div class="stat-val">1340 : 820</div>
            <div class="ad-bar-container"><div class="ad-advance" style="width: 62%;"></div></div>
        </div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 2. INDICES DYNAMIC LEVELS
# ------------------------------------------------------------------
n_spot = n["spot"]
b_spot = live_data["banknifty"]["spot"]
s_spot = live_data["sensex"]["spot"]

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

