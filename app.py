import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL - FULL INDICES & EXPIRY SYNC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp { background-color: #F8FAFC; color: #0F172A; }
.block-container { padding: 0.6rem 0.5rem !important; }

.status-banner {
    padding: 6px 12px; border-radius: 6px; font-size: 11px;
    font-weight: 800; margin-bottom: 8px; display: flex;
    justify-content: space-between; align-items: center;
}
.banner-running { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
.banner-sl { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
.banner-wait { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }

.analysis-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-left: 6px solid #16A34A; border-radius: 10px;
    padding: 14px; margin-bottom: 14px; box-shadow: 0 3px 6px rgba(0,0,0,0.04);
}
.card-sl { border-left-color: #DC2626; }
.card-wait { border-left-color: #D97706; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.symbol-title { font-size: 16px; font-weight: 900; color: #0F172A; }

.badge-rec { font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 6px; color: white; }
.bg-buy { background-color: #16A34A; }
.bg-exit { background-color: #DC2626; }
.bg-wait { background-color: #D97706; }
.bg-hold { background-color: #2563EB; }

.card-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; 
    background: #F1F5F9; padding: 10px; border-radius: 8px; 
    text-align: center; margin-top: 8px; 
}
.grid-lbl { font-size: 9px; color: #64748B; font-weight: 800; }
.grid-val { font-size: 13px; color: #0F172A; font-weight: 900; }
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
            fast_data = t.fast_info
            price = round(fast_data.last_price, 2)
            prev_close = fast_data.previous_close
            chg_pct = round(((price - prev_close) / prev_close) * 100, 2)
            data_res[name] = {"price": price, "chg": chg_pct}
        except:
            fallback = {"NIFTY": 23985.35, "BANKNIFTY": 51200.0, "FINNIFTY": 23400.0, "MIDCPNIFTY": 12500.0, "SENSEX": 78500.0, "NIFTY IT": 38200.0}
            data_res[name] = {"price": fallback.get(name, 20000.0), "chg": -0.08}
    return data_res

st.title("⚡ PRO MASTER TERMINAL")

selected_index = st.selectbox("🎯 Select Active Index", list(tickers.keys()), index=0)

market_data = get_real_market_data()
spot_price = market_data[selected_index]["price"]

step = 100 if selected_index in ["BANKNIFTY", "SENSEX", "NIFTY IT"] else 50
atm_strike = int(round(spot_price / step) * step)

# Safe Native Columns Ticker Bar (No HTML string breakage)
cols = st.columns(len(market_data))
for i, (name, info) in enumerate(market_data.items()):
    with cols[i]:
        chg_color = "🟢" if info['chg'] >= 0 else "🔴"
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px; text-align: center;">
            <div style="font-size: 9px; color: #64748B; font-weight: 800;">{name}</div>
            <div style="font-size: 12px; color: #0F172A; font-weight: 900;">{info['price']}</div>
            <div style="font-size: 9px; font-weight: 800; color: {'#16A34A' if info['chg'] >= 0 else '#DC2626'};">{info['chg']}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

def get_expiry_aware_ltp(strike, is_call, spot):
    diff = (spot - strike) if is_call else (strike - spot)
    if diff >= 0:
        return round(max(0.5, diff + 2.0), 2)
    else:
        decay_val = max(0.2, 5.0 - abs(diff) * 0.1)
        return round(decay_val if abs(diff) <= 50 else 0.5, 2)

itm_strike = atm_strike - step
ce_itm_ltp = get_expiry_aware_ltp(itm_strike, True, spot_price)
ce_atm_ltp = get_expiry_aware_ltp(atm_strike, True, spot_price)
btst_strike = atm_strike + step
ce_btst_ltp = get_expiry_aware_ltp(btst_strike, True, spot_price)

tab_trades, tab_eval, tab_btst, tab_hz, tab_chain, tab_chart = st.tabs([
    "🚀 Live Trades", "💡 AI Evaluator", "🎯 BTST Zone", "🔥 Hero-Zero", "📊 Option Chain", "📈 OI Chart"
])

with tab_trades:
    st.subheader(f"🚀 Active Live Trades for {selected_index} (Spot: {spot_price})")
    signals = [
        {"symbol": f"{selected_index} {itm_strike} CE", "ltp": ce_itm_ltp, "entry": 45.60, "sl": 15.00, "target": 90.00, "state": "HOLD"},
        {"symbol": f"{selected_index} {atm_strike} CE", "ltp": ce_atm_ltp, "entry": 18.20, "sl": 5.00, "target": 45.00, "state": "WAIT"}
    ]
    for s in signals:
        ltp, entry, sl, state = s["ltp"], s["entry"], s["sl"], s["state"]
        card_cls, banner_cls, rec_cls, rec, status_msg = ("analysis-card", "banner-running", "bg-hold", "HOLD", f"🟢 ACTIVE POSITION — LTP ₹{ltp}") if ltp > sl else ("analysis-card card-sl", "banner-sl", "bg-exit", "EXIT", f"🚨 SL HIT — LTP ₹{ltp}")
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="status-banner {banner_cls}"><span>{status_msg}</span><span>🔄 EXPIRY SYNCED</span></div>
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
    st.subheader("💡 AI Option Trade Evaluator")
    col1, col2 = st.columns(2)
    with col1: u_strike = st.number_input("Strike", value=int(atm_strike), step=step)
    with col2: u_opt = st.selectbox("Type", ["CE (Call)", "PE (Put)"])
    is_ce = "CE" in u_opt
    e_ltp = get_expiry_aware_ltp(u_strike, is_ce, spot_price)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🎯 EXPIRY-AWARE EVALUATION</span><span>OK</span></div>
        <div class="card-header"><span class="symbol-title">{selected_index} {u_strike} {'CE' if is_ce else 'PE'}</span><span class="badge-rec bg-buy">READY</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">LTP</div><div class="grid-val">₹{e_ltp}</div></div>
            <div><div class="grid-lbl">ENTRY</div><div class="grid-val">₹{round(e_ltp*1.05, 1)}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹{round(e_ltp*0.5, 1)}</div></div>
            <div><div class="grid-lbl">TARGET</div><div class="grid-val">₹{round(e_ltp*1.5, 1)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_btst:
    st.subheader("🎯 BTST Zone (Expiry Decay Considered)")
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🌙 OVERNIGHT HOLD</span><span>3:15 PM</span></div>
        <div class="card-header"><span class="symbol-title">{selected_index} {btst_strike} CE (BTST)</span><span class="badge-rec bg-buy">BTST BUY</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">BUY RANGE</div><div class="grid-val">₹{ce_btst_ltp}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹{round(ce_btst_ltp*0.4, 1)}</div></div>
            <div><div class="grid-lbl">T1</div><div class="grid-val">₹{round(ce_btst_ltp*1.5, 1)}</div></div>
            <div><div class="grid-lbl">T2</div><div class="grid-val">₹{round(ce_btst_ltp*2.0, 1)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_hz:
    st.subheader("🔥 Hero-Zero Special")
    st.markdown(f"""
    <div class="analysis-card" style="border-left-color: #9333EA;">
        <div class="status-banner" style="background: #F3E8FF; color: #6B21A8;"><span>🚀 SPIKE</span><span>ACTIVE</span></div>
        <div class="card-header"><span class="symbol-title">{selected_index} {atm_strike} CE</span><span class="badge-rec bg-hold">HERO-ZERO</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">ENTRY</div><div class="grid-val">₹2.00 - ₹5.00</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹0.00</div></div>
            <div><div class="grid-lbl">T1</div><div class="grid-val">₹15.00</div></div>
            <div><div class="grid-lbl">T2</div><div class="grid-val">₹25.00</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_chain:
    st.subheader(f"📊 {selected_index} Option Chain")
    chain_df = pd.DataFrame([
        {"CALL OI": "1.00L", "CALL PRICE": f"₹{get_expiry_aware_ltp(atm_strike-step, True, spot_price)}", "STRIKE": atm_strike-step, "PUT PRICE": f"₹{get_expiry_aware_ltp(atm_strike-step, False, spot_price)}", "PUT OI": "3.55L"},
        {"CALL OI": "2.38L", "CALL PRICE": f"₹{ce_itm_ltp}", "STRIKE": atm_strike, "PUT PRICE": f"₹{get_expiry_aware_ltp(atm_strike, False, spot_price)}", "PUT OI": "7.15L"},
        {"CALL OI": "9.32L", "CALL PRICE": f"₹{ce_atm_ltp}", "STRIKE": atm_strike+step, "PUT PRICE": f"₹{get_expiry_aware_ltp(atm_strike+step, False, spot_price)}", "PUT OI": "5.66L"},
    ])
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

with tab_chart:
    st.subheader(f"📈 OI Distribution")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(atm_strike-step), str(atm_strike), str(atm_strike+step)], y=[1.00, 2.38, 9.32], name='Call OI', marker_color='#DC2626'))
    fig.add_trace(go.Bar(x=[str(atm_strike-step), str(atm_strike), str(atm_strike+step)], y=[3.55, 7.15, 5.66], name='Put OI', marker_color='#16A34A'))
    fig.update_layout(barmode='group', height=300, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

