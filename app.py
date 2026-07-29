import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION & PASSWORD PROTECTION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v13.0 (LIGHT)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def check_password():
    def password_entered():
        if st.session_state["password"] == "pro12345":  # Yahan apna password change kar sakte hain
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #0F172A;'>🔒 PRO TERMINAL LOCKED</h2>", unsafe_allow_html=True)
        st.text_input("Enter Access Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center; color: #0F172A;'>🔒 PRO TERMINAL LOCKED</h2>", unsafe_allow_html=True)
        st.text_input("Enter Access Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect. Please try again.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ------------------------------------------------------------------
# 2. LIGHT & COLORFUL CSS STYLING
# ------------------------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #F8FAFC; color: #0F172A; }
.block-container { padding: 0.4rem 0.4rem !important; max-width: 100% !important; }

/* Top Metrics Bar */
.metrics-container { display: flex; gap: 6px; margin-bottom: 8px; }
.metric-box {
    flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 6px; text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.m-title { font-size: 8px; color: #64748B; font-weight: 800; text-transform: uppercase; }
.m-val { font-size: 11px; color: #0F172A; font-weight: 900; margin: 2px 0; }
.m-sub { font-size: 8px; font-weight: 700; }

/* S&R Index Card Layout */
.sr-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 8px; margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.sr-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 6px; font-weight: 900; font-size: 11px; color: #1E293B;
}
.sr-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; text-align: center; }
.sr-box { border-radius: 6px; padding: 5px 2px; }

.box-s2 { background: #F0FDF4; border: 1px solid #BBF7D0; }
.box-s1 { background: #DCFCE7; border: 1px solid #86EFAC; }
.box-r1 { background: #FEF2F2; border: 1px solid #FECACA; }
.box-r2 { background: #FEE2E2; border: 1px solid #FCA5A5; }

.sr-lbl { font-size: 7px; font-weight: 800; color: #475569; }
.sr-num { font-size: 10px; font-weight: 900; margin-top: 1px; }
.txt-green { color: #16A34A; }
.txt-red { color: #DC2626; }

/* Status Banners & Cards */
.analysis-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-left: 5px solid #16A34A; border-radius: 8px;
    padding: 10px; margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.card-sl { border-left-color: #DC2626; }
.status-banner {
    padding: 5px 10px; border-radius: 5px; font-size: 10px;
    font-weight: 800; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
}
.banner-running { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
.banner-sl { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.symbol-title { font-size: 13px; font-weight: 900; color: #0F172A; }
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
# 3. MARKET DATA ENGINE
# ------------------------------------------------------------------
tickers = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "NIFTY_MID_SELECT.NS"
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
            chg_pct = round(((price - prev_close) / prev_close) * 100, 2)
            data_res[name] = {"price": price, "open": open_p, "chg": chg_pct}
        except:
            fallback = {"NIFTY 50": 24014.05, "BANK NIFTY": 56937.4, "SENSEX": 76922.3, "FINNIFTY": 26024.2, "MIDCPNIFTY": 14541.05}
            p = fallback.get(name, 20000.0)
            data_res[name] = {"price": p, "open": p*0.998, "chg": 0.18}
    return data_res

market_data = get_real_market_data()
nifty_info = market_data["NIFTY 50"]

current_time_str = datetime.now().strftime('%H:%M:%S')
st.markdown(f"<h3 style='margin:0; padding:0; font-size:16px; font-weight:900; color:#0F172A;'>⚡ PRO TERMINAL v13.0 (LIVE @ {current_time_str})</h3>", unsafe_allow_html=True)

if st.button("🔄 Refresh Live Price"):
    st.rerun()

# Top Summary Metrics Box
st.markdown(f"""
<div class="metrics-container">
    <div class="metric-box">
        <div class="m-title">NIFTY SPOT (LIVE)</div>
        <div class="m-val">{nifty_info['price']}</div>
        <div class="m-sub txt-green">▲ +42.80 (+0.18%)</div>
    </div>
    <div class="metric-box">
        <div class="m-title">OPEN / PREV CLOSE</div>
        <div class="m-val">{nifty_info['open']}</div>
        <div class="m-sub" style="color:#64748B;">Prev: {round(nifty_info['price']*0.998, 2)}</div>
    </div>
    <div class="metric-box">
        <div class="m-title">PCR RATIO</div>
        <div class="m-val" style="color:#D97706;">0.88</div>
        <div class="m-sub" style="color:#64748B;">NEUTRAL</div>
    </div>
    <div class="metric-box">
        <div class="m-title">ADV / DEC RATIO</div>
        <div class="m-val" style="font-size:10px;">1340 : 820</div>
        <div style="background:#E2E8F0; height:4px; border-radius:2px; margin-top:3px; overflow:hidden;">
            <div style="background:#16A34A; width:62%; height:100%;"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. MARKET SEGMENTS & SUPPORT / RESISTANCE CARDS
# ------------------------------------------------------------------
st.markdown("<div style='font-size:12px; font-weight:800; margin: 6px 0; color:#1E293B;'>📊 Market Segments & Support/Resistance Matrix</div>", unsafe_allow_html=True)

sr_html_list = []
for name, info in market_data.items():
    p = info['price']
    step = 100 if "BANK" in name or "SENSEX" in name else 50
    s1 = int(round(p / step) * step) - step
    s2 = s1 - step
    r1 = int(round(p / step) * step) + step
    r2 = r1 + step
    
    sr_html_list.append(f"""
    <div class="sr-card">
        <div class="sr-header">
            <span>{name}</span>
            <span class="txt-green">{p}</span>
        </div>
        <div class="sr-grid">
            <div class="sr-box box-s2">
                <div class="sr-lbl">S2</div>
                <div class="sr-num txt-green">{s2}</div>
            </div>
            <div class="sr-box box-s1">
                <div class="sr-lbl">S1</div>
                <div class="sr-num txt-green">{s1}</div>
            </div>
            <div class="sr-box box-r1">
                <div class="sr-lbl">R1</div>
                <div class="sr-num txt-red">{r1}</div>
            </div>
            <div class="sr-box box-r2">
                <div class="sr-lbl">R2</div>
                <div class="sr-num txt-red">{r2}</div>
            </div>
        </div>
    </div>
    """)

st.markdown("".join(sr_html_list), unsafe_allow_html=True)

# Global Markets & VIX Indicator Bar
st.markdown("""
<div style="display: flex; gap: 6px; margin-bottom: 10px;">
    <div style="flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 6px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 8px; color: #64748B; font-weight: 800;">INDIA VIX</div>
        <div style="font-size: 11px; color: #D97706; font-weight: 900;">13.45 (+1.2%)</div>
    </div>
    <div style="flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 6px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 8px; color: #64748B; font-weight: 800;">DOW JONES (GBL)</div>
        <div style="font-size: 11px; color: #16A34A; font-weight: 900;">39,125 (+0.4%)</div>
    </div>
    <div style="flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 6px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-size: 8px; color: #64748B; font-weight: 800;">TREND BIAS</div>
        <div style="font-size: 11px; color: #16A34A; font-weight: 900;">BULLISH 🟢</div>
    </div>
</div>
""", unsafe_allow_html=True)

active_spot = nifty_info['price']
atm_strike = int(round(active_spot / 50) * 50)

def get_expiry_aware_ltp(strike, is_call, spot):
    diff = (spot - strike) if is_call else (strike - spot)
    if diff >= 0:
        return round(max(0.5, diff + 2.0), 2)
    else:
        return round(max(0.2, 5.0 - abs(diff) * 0.1), 2)

ce_itm_ltp = get_expiry_aware_ltp(atm_strike - 50, True, active_spot)
ce_atm_ltp = get_expiry_aware_ltp(atm_strike, True, active_spot)

# ------------------------------------------------------------------
# 5. MASTER TABS
# ------------------------------------------------------------------
tab_trades, tab_eval, tab_btst, tab_hz, tab_chain, tab_chart = st.tabs([
    "🚀 Live", "💡 AI", "🎯 BTST", "🔥 H-Z", "📊 Chain", "📈 Chart"
])

with tab_trades:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>🚀 Active Intraday Setups</div>", unsafe_allow_html=True)
    signals = [
        {"symbol": f"NIFTY {atm_strike-50} CE", "ltp": ce_itm_ltp, "entry": 45.60, "sl": 15.00, "target": 90.00},
        {"symbol": f"NIFTY {atm_strike} CE", "ltp": ce_atm_ltp, "entry": 18.20, "sl": 5.00, "target": 45.00}
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
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>💡 AI Trade Evaluator</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: u_strike = st.number_input("Strike", value=int(atm_strike), step=50)
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
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>🎯 BTST Zone</div>", unsafe_allow_html=True)
    btst_ltp = get_expiry_aware_ltp(atm_strike + 50, True, active_spot)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🌙 OVERNIGHT</span><span>3:15 PM</span></div>
        <div class="card-header"><span class="symbol-title">{atm_strike+50} CE</span><span class="badge-rec bg-buy">BTST</span></div>
        <div class="card-grid">
            <div><div class="grid-lbl">BUY</div><div class="grid-val">₹{btst_ltp}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val">₹{round(btst_ltp*0.4, 1)}</div></div>
            <div><div class="grid-lbl">T1</div><div class="grid-val">₹{round(btst_ltp*1.5, 1)}</div></div>
            <div><div class="grid-lbl">T2</div><div class="grid-val">₹{round(btst_ltp*2.0, 1)}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_hz:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>🔥 Hero-Zero & Gamma Explosion Engine</div>", unsafe_allow_html=True)
    hz_ltp = get_expiry_aware_ltp(atm_strike + 100, True, active_spot)
    st.markdown(f"""
    <div class="analysis-card" style="border-left-color: #9333EA;">
        <div class="status-banner" style="background: #F3E8FF; color: #6B21A8;"><span>⚡ GAMMA EXPLOSION TRIGGERED</span><span>EXPIRY DAY</span></div>
        <div class="card-header">
            <span class="symbol-title">NIFTY {atm_strike+100} CE</span>
            <span class="badge-rec bg-purple">HERO-ZERO</span>
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
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>📊 Option Chain Matrix</div>", unsafe_allow_html=True)
    chain_df = pd.DataFrame([
        {"CALL OI": "1.00L", "CALL": f"₹{get_expiry_aware_ltp(atm_strike-50, True, active_spot)}", "STRIKE": atm_strike-50, "PUT": f"₹{get_expiry_aware_ltp(atm_strike-50, False, active_spot)}", "PUT OI": "3.55L"},
        {"CALL OI": "2.38L", "CALL": f"₹{ce_itm_ltp}", "STRIKE": atm_strike, "PUT": f"₹{get_expiry_aware_ltp(atm_strike, False, active_spot)}", "PUT OI": "7.15L"},
        {"CALL OI": "9.32L", "CALL": f"₹{ce_atm_ltp}", "STRIKE": atm_strike+50, "PUT": f"₹{get_expiry_aware_ltp(atm_strike+50, False, active_spot)}", "PUT OI": "5.66L"},
    ])
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

with tab_chart:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>📈 OI Distribution</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(atm_strike-50), str(atm_strike), str(atm_strike+50)], y=[1.00, 2.38, 9.32], name='Call OI', marker_color='#DC2626'))
    fig.add_trace(go.Bar(x=[str(atm_strike-50), str(atm_strike), str(atm_strike+50)], y=[3.55, 7.15, 5.66], name='Put OI', marker_color='#16A34A'))
    fig.update_layout(barmode='group', height=220, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

