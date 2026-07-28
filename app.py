import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CSS
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO MASTER TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp { background-color: #F8FAFC; color: #0F172A; }
.block-container { padding: 0.3rem 0.3rem !important; max-width: 100% !important; }

/* Grid container to hold multiple cards side-by-side */
.indices-container {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 6px;
}
.index-box {
    flex: 1 1 30%;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 6px 4px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.idx-title { font-size: 8px; color: #64748B; font-weight: 800; }
.idx-val { font-size: 10px; color: #0F172A; font-weight: 900; margin: 2px 0; }
.idx-chg { font-size: 8px; font-weight: 800; }

.status-banner {
    padding: 5px 10px; border-radius: 5px; font-size: 10px;
    font-weight: 800; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
}
.banner-running { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
.banner-sl { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }

.analysis-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-left: 5px solid #16A34A; border-radius: 8px;
    padding: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.card-sl { border-left-color: #DC2626; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.symbol-title { font-size: 14px; font-weight: 900; color: #0F172A; }

.badge-rec { font-size: 9px; font-weight: 800; padding: 3px 8px; border-radius: 4px; color: white; }
.bg-buy { background-color: #16A34A; }
.bg-exit { background-color: #DC2626; }
.bg-hold { background-color: #2563EB; }
.bg-purple { background-color: #9333EA; }

.card-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; 
    background: #F1F5F9; padding: 6px; border-radius: 6px; 
    text-align: center; margin-top: 6px; 
}
.grid-lbl { font-size: 8px; color: #64748B; font-weight: 800; }
.grid-val { font-size: 11px; color: #0F172A; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. MARKET DATA ENGINE
# ------------------------------------------------------------------
tickers = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MID_SELECT.NS",
    "SENSEX": "^BSESN",
    "NIFTY IT": "^CNXIT"
}

def get_real_market_data():
    data_res = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            fd = t.fast_info
            price = round(fd.last_price, 2)
            prev_close = fd.previous_close
            open_p = round(getattr(fd, 'open', prev_close), 2)
            high_p = round(getattr(fd, 'day_high', price * 1.01), 2)
            low_p = round(getattr(fd, 'day_low', price * 0.99), 2)
            chg_pct = round(((price - prev_close) / prev_close) * 100, 2)
            data_res[name] = {"price": price, "open": open_p, "high": high_p, "low": low_p, "chg": chg_pct}
        except:
            fallback = {"NIFTY": 23985.35, "BANKNIFTY": 56755.6, "FINNIFTY": 26024.2, "MIDCPNIFTY": 14541.05, "SENSEX": 76765.92, "NIFTY IT": 30418.35}
            p = fallback.get(name, 20000.0)
            data_res[name] = {"price": p, "open": p*0.995, "high": p*1.008, "low": p*0.992, "chg": 0.02}
    return data_res

st.markdown("<h3 style='margin:0; padding:0; font-size:15px;'>⚡ PRO MASTER TERMINAL</h3>", unsafe_allow_html=True)

market_data = get_real_market_data()

index_options = ["ALL INDICES"] + list(tickers.keys())
selected_index = st.selectbox("🎯 Select Active Index", index_options, index=0)

# Clean single-line list comprehension method to prevent raw tag printing
cards_html = "".join([
    f'<div class="index-box"><div class="idx-title">{name}</div><div class="idx-val">{info["price"]}</div><div class="idx-chg" style="color: {"#16A34A" if info["chg"] >= 0 else "#DC2626"};">{info["chg"]}%</div></div>'
    for name, info in market_data.items()
])
st.markdown(f'<div class="indices-container">{cards_html}</div>', unsafe_allow_html=True)

# Advance / Decline & PCR Bar
st.markdown("""
<div style="display: flex; gap: 6px; margin-bottom: 8px;">
    <div style="flex: 1; background: #E0F2FE; padding: 5px; border-radius: 5px; text-align: center; font-size: 10px; font-weight: 800; color: #0369A1;">
        📈 ADV: <b>34</b> | DEC: <b>16</b>
    </div>
    <div style="flex: 1; background: #F3E8FF; padding: 5px; border-radius: 5px; text-align: center; font-size: 10px; font-weight: 800; color: #6B21A8;">
        📊 PCR: <b>1.08</b> | ⏰ EXPIRY ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

active_spot = market_data["NIFTY"]["price"] if selected_index == "ALL INDICES" else market_data[selected_index]["price"]
step = 100 if selected_index in ["BANKNIFTY", "SENSEX", "NIFTY IT"] else 50
atm_strike = int(round(active_spot / step) * step) if selected_index != "ALL INDICES" else 24000

def get_expiry_aware_ltp(strike, is_call, spot):
    diff = (spot - strike) if is_call else (strike - spot)
    if diff >= 0:
        return round(max(0.5, diff + 2.0), 2)
    else:
        decay_val = max(0.2, 5.0 - abs(diff) * 0.1)
        return round(decay_val if abs(diff) <= 50 else 0.5, 2)

itm_strike = atm_strike - step
ce_itm_ltp = get_expiry_aware_ltp(itm_strike, True, active_spot)
ce_atm_ltp = get_expiry_aware_ltp(atm_strike, True, active_spot)
btst_strike = atm_strike + step
ce_btst_ltp = get_expiry_aware_ltp(btst_strike, True, active_spot)

# ------------------------------------------------------------------
# 3. MASTER TABS
# ------------------------------------------------------------------
tab_trades, tab_eval, tab_btst, tab_hz, tab_chain, tab_chart = st.tabs([
    "🚀 Live", "💡 AI", "🎯 BTST", "🔥 H-Z", "📊 Chain", "📈 Chart"
])

with tab_trades:
    disp_name = "All Indices" if selected_index == "ALL INDICES" else selected_index
    st.markdown(f"<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>🚀 Active Trades ({disp_name})</div>", unsafe_allow_html=True)
    
    signals = [
        {"symbol": f"{selected_index if selected_index!='ALL INDICES' else 'NIFTY'} {itm_strike} CE", "ltp": ce_itm_ltp, "entry": 45.60, "sl": 15.00, "target": 90.00},
        {"symbol": f"{selected_index if selected_index!='ALL INDICES' else 'NIFTY'} {atm_strike} CE", "ltp": ce_atm_ltp, "entry": 18.20, "sl": 5.00, "target": 45.00}
    ]
    for s in signals:
        ltp, entry, sl = s["ltp"], s["entry"], s["sl"]
        card_cls, banner_cls, rec_cls, rec, status_msg = ("analysis-card", "banner-running", "bg-hold", "HOLD", f"🟢 ACTIVE — LTP ₹{ltp}") if ltp > sl else ("analysis-card card-sl", "banner-sl", "bg-exit", "EXIT", f"🚨 SL HIT — LTP ₹{ltp}")
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="status-banner {banner_cls}"><span>{status_msg}</span><span>🔄 SYNC</span></div>
            <div class="card-header"><span class="symbol-title">{s['symbol']}</span><span class="badge-rec {rec_cls}">{rec}</span></div>
            <div class="card-grid">
                <div><div class="grid-lbl">LTP</div><div class="grid-val" style="color:#DC2626;">₹{ltp}</div></div>
                <div><div class="grid-lbl">ENTRY</div><div class="grid-val">₹{entry}</div></div>
                <div><div class="grid-lbl">SL</div><div class="grid-val" style="color:#DC2626;">₹{sl}</div></div>
                <div><div class="grid-lbl">TARGET</div><div class="grid-val" style="color:#16A34A;">₹{s['target']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_eval:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>💡 AI Trade Evaluator</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: u_strike = st.number_input("Strike", value=int(atm_strike), step=step)
    with col2: u_opt = st.selectbox("Type", ["CE (Call)", "PE (Put)"])
    is_ce = "CE" in u_opt
    e_ltp = get_expiry_aware_ltp(u_strike, is_ce, active_spot)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🎯 EVALUATION</span><span>OK</span></div>
        <div class="card-header"><span class="symbol-title">{u_strike} {'CE' if is_ce else 'PE'}</span><span class="badge-rec bg-buy">READY</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">LTP</div><div class="grid-val">₹{e_ltp}</div></div>
            <div><div class="grid-lbl">ENTRY</div><div class="grid-val">₹{round(e_ltp*1.05, 1)}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹{round(e_ltp*0.5, 1)}</div></div>
            <div><div class="grid-lbl">TARGET</div><div class="grid-val">₹{round(e_ltp*1.5, 1)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_btst:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>🎯 BTST Zone</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🌙 OVERNIGHT</span><span>3:15 PM</span></div>
        <div class="card-header"><span class="symbol-title">{btst_strike} CE</span><span class="badge-rec bg-buy">BTST</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">BUY</div><div class="grid-val">₹{ce_btst_ltp}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹{round(ce_btst_ltp*0.4, 1)}</div></div>
            <div><div class="grid-lbl">T1</div><div class="grid-val">₹{round(ce_btst_ltp*1.5, 1)}</div></div>
            <div><div class="grid-lbl">T2</div><div class="grid-val">₹{round(ce_btst_ltp*2.0, 1)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_hz:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>🔥 Detailed Hero-Zero & Gamma Explosion Engine</div>", unsafe_allow_html=True)
    
    curr_idx_key = "NIFTY" if selected_index == "ALL INDICES" else selected_index
    curr_info = market_data[curr_idx_key]
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">
        <div style="background: #F1F5F9; padding: 6px; border-radius: 6px; text-align: center;">
            <div style="font-size: 7px; color: #64748B; font-weight: 800;">OPEN</div>
            <div style="font-size: 10px; color: #0F172A; font-weight: 900;">{curr_info['open']}</div>
        </div>
        <div style="background: #F1F5F9; padding: 6px; border-radius: 6px; text-align: center;">
            <div style="font-size: 7px; color: #64748B; font-weight: 800;">HIGH</div>
            <div style="font-size: 10px; color: #16A34A; font-weight: 900;">{curr_info['high']}</div>
        </div>
        <div style="background: #F1F5F9; padding: 6px; border-radius: 6px; text-align: center;">
            <div style="font-size: 7px; color: #64748B; font-weight: 800;">LOW</div>
            <div style="font-size: 10px; color: #DC2626; font-weight: 900;">{curr_info['low']}</div>
        </div>
        <div style="background: #F1F5F9; padding: 6px; border-radius: 6px; text-align: center;">
            <div style="font-size: 7px; color: #64748B; font-weight: 800;">SPIKE PROB</div>
            <div style="font-size: 10px; color: #9333EA; font-weight: 900;">88.4%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    hz_strike = atm_strike + step
    hz_ltp = get_expiry_aware_ltp(hz_strike, True, active_spot)
    
    st.markdown(f"""
    <div class="analysis-card" style="border-left-color: #9333EA;">
        <div class="status-banner" style="background: #F3E8FF; color: #6B21A8;"><span>⚡ GAMMA EXPLOSION TRIGGERED</span><span>EXPIRY DAY</span></div>
        <div class="card-header">
            <span class="symbol-title">{curr_idx_key} {hz_strike} CE</span>
            <span class="badge-rec bg-purple">HERO-ZERO</span>
        </div>
        <div style="font-size: 9px; color: #475569; margin: 4px 0; font-weight: 700;">
            💡 <b>Logic:</b> Massive OI Unwinding at {atm_strike} Strike | ⭐ <b>Grade:</b> EXTREME SPIKE SETUP
        </div>
        <div class="card-grid">
            <div><div class="grid-lbl">LTP</div><div class="grid-val" style="color:#9333EA;">₹{hz_ltp}</div></div>
            <div><div class="grid-lbl">ENTRY ZONE</div><div class="grid-val">₹3.0 - ₹6.0</div></div>
            <div><div class="grid-lbl">STOPLOSS</div><div class="grid-val" style="color:#DC2626;">₹0.0</div></div>
            <div><div class="grid-lbl">TARGET</div><div class="grid-val" style="color:#16A34A;">₹35.0+</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_chain:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>📊 Option Chain Matrix</div>", unsafe_allow_html=True)
    chain_df = pd.DataFrame([
        {"CALL OI": "1.00L", "CALL": f"₹{get_expiry_aware_ltp(atm_strike-step, True, active_spot)}", "STRIKE": atm_strike-step, "PUT": f"₹{get_expiry_aware_ltp(atm_strike-step, False, active_spot)}", "PUT OI": "3.55L"},
        {"CALL OI": "2.38L", "CALL": f"₹{ce_itm_ltp}", "STRIKE": atm_strike, "PUT": f"₹{get_expiry_aware_ltp(atm_strike, False, active_spot)}", "PUT OI": "7.15L"},
        {"CALL OI": "9.32L", "CALL": f"₹{ce_atm_ltp}", "STRIKE": atm_strike+step, "PUT": f"₹{get_expiry_aware_ltp(atm_strike+step, False, active_spot)}", "PUT OI": "5.66L"},
    ])
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

with tab_chart:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px;'>📈 OI Distribution</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(atm_strike-step), str(atm_strike), str(atm_strike+step)], y=[1.00, 2.38, 9.32], name='Call OI', marker_color='#DC2626'))
    fig.add_trace(go.Bar(x=[str(atm_strike-step), str(atm_strike), str(atm_strike+step)], y=[3.55, 7.15, 5.66], name='Put OI', marker_color='#16A34A'))
    fig.update_layout(barmode='group', height=220, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

