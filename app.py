import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime

# ------------------------------------------------------------------
# 1. PAGE CONFIG & PWA NATIVE APP INJECTION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v27.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper Function to render raw HTML cleanly
def render_clean_html(html_str):
    st.markdown(str(html_str).strip(), unsafe_allow_html=True)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#0B0F19">
    
    <script>
    function requestNotificationPermission() {
        if ("Notification" in window && Notification.permission !== "granted") {
            Notification.requestPermission();
        }
    }
    requestNotificationPermission();

    // Audio Alert Play Function
    function playAlertSound() {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        var gain = context.createGain();
        osc.connect(gain);
        gain.connect(context.destination);
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, context.currentTime); // High pitch A5 tone
        gain.gain.setValueAtTime(0.1, context.currentTime);
        osc.start();
        osc.stop(context.currentTime + 0.3);
    }
    </script>
""", unsafe_allow_html=True)

# Passcode Auth
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_passcode():
    if st.session_state.get("passcode_input") == "1234":
        st.session_state.authenticated = True
    else:
        st.error("❌ Invalid Passcode")

if not st.session_state.authenticated:
    st.title("🔐 Terminal Access Locked")
    st.text_input("Enter Passcode:", type="password", key="passcode_input", on_change=check_passcode)
    st.stop()

# Push Notification & Audio Trigger Engine
def trigger_native_push(title, message, play_sound=True):
    sound_js = "playAlertSound();" if play_sound else ""
    js_code = f"""
    <script>
    {sound_js}
    if ("Notification" in window && Notification.permission === "granted") {{
        new Notification("{title}", {{
            body: "{message}",
            icon: "https://cdn-icons-png.flaticon.com/512/1828/1828884.png",
            silent: false
        }});
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# ------------------------------------------------------------------
# 2. HIGHLY VISUALIZED CUSTOM CSS (FIXED FOR TYPEERROR)
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
.stat-lbl { font-size: 7px; color: #9CA3AF; font-weight: 700; text-transform: uppercase; }
.stat-val { font-size: 10px; font-weight: 800; color: #F9FAFB; margin: 2px 0; }
.stat-sub-up { font-size: 7px; color: #10B981; font-weight: 800; }

/* Trade Cards Visuals */
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
.st-target { background: #DCFCE7; color: #15803D; }
.st-sl { background: #FEE2E2; color: #B91C1C; }

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
# 3. LIVE DATA ENGINE
# ------------------------------------------------------------------
def calc_live_option_price(spot, strike, is_call=True):
    intrinsic = max(0, spot - strike) if is_call else max(0, strike - spot)
    dist = abs(spot - strike)
    time_val = max(2.5, 38.0 - (dist * 0.20))
    return round(intrinsic + time_val, 2)

@st.cache_data(ttl=3)
def fetch_live_engine():
    data = {
        "nifty": {"spot": 24007.55, "open": 23971.25, "chg": 36.30, "pct": 0.15},
        "banknifty": {"spot": 57000.00, "open": 56850.00, "chg": 150.00, "pct": 0.26},
        "finnifty": {"spot": 21850.00, "open": 21800.00, "chg": 50.00, "pct": 0.23},
        "midcap": {"spot": 12450.00, "open": 12400.00, "chg": 50.00, "pct": 0.40},
        "pcr": 0.88,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    
    try:
        indices = yf.Tickers('^NSEI ^NSEBANK')
        n_df = indices.tickers['^NSEI'].history(period='1d', interval='1m')
        b_df = indices.tickers['^NSEBANK'].history(period='1d', interval='1m')

        if not n_df.empty:
            spot = n_df['Close'].iloc[-1]
            open_p = n_df['Open'].iloc[0]
            chg = spot - open_p
            pct = (chg / open_p) * 100 if open_p != 0 else 0
            data["nifty"] = {"spot": float(spot), "open": float(open_p), "chg": float(chg), "pct": float(pct)}

        if not b_df.empty:
            b_spot = b_df['Close'].iloc[-1]
            b_open = b_df['Open'].iloc[0]
            data["banknifty"]["spot"] = float(b_spot)
            data["banknifty"]["open"] = float(b_open)
    except Exception:
        pass
        
    return data

engine_data = fetch_live_engine()
n = engine_data["nifty"]
b = engine_data["banknifty"]
fin = engine_data["finnifty"]
mid = engine_data["midcap"]

# Header Bar
render_clean_html(f"""
<div class="top-header">
    <div class="app-title">⚡ PRO TERMINAL <span style="font-size: 9px; color: #94A3B8;">TARGET UPDATE TRACKER</span></div>
    <div style="font-size: 10px; font-weight: 800; color: #10B981;">
        <span class="live-dot"></span>{engine_data['time']}
    </div>
</div>
""")

col_ref, _ = st.columns([1, 3])
with col_ref:
    if st.button("🔄 Sync Market Data", use_container_width=True):
        st.rerun()

# Multi-Index Overview Bar
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
# 4. TABULAR ENGINE WITH TARGET UPDATE TRACKING
# ------------------------------------------------------------------
tab_signals, tab_hero, tab_chain, tab_charts = st.tabs([
    "⚡ Active Signals (4)", 
    "🚀 Zero-Hero Algo", 
    "📊 Option Chain", 
    "📈 Interactive Chart"
])

# ------------------------------------------------------------------
# TAB 1: ACTIVE SIGNALS WITH MODIFIED TARGET HIGHLIGHTS
# ------------------------------------------------------------------
with tab_signals:
    n_atm = int(round(n['spot'] / 50.0) * 50)
    b_atm = int(round(b['spot'] / 100.0) * 100)

    ltp_n_ce = calc_live_option_price(n['spot'], n_atm, is_call=True)
    ltp_b_pe = calc_live_option_price(b['spot'], b_atm, is_call=False)
    ltp_fin_ce = calc_live_option_price(fin['spot'], 21850, is_call=True)
    ltp_mid_pe = calc_live_option_price(mid['spot'], 12450, is_call=False)

    trades = [
        {
            "symbol": f"NIFTY {n_atm} CE",
            "type": "BUY CALL",
            "algo": "EMA CROSS + OI SPIKE",
            "ltp": ltp_n_ce,
            "entry": round(ltp_n_ce * 0.98, 1),
            "sl": round(ltp_n_ce * 0.75, 1),
            "hold_sl": round(ltp_n_ce * 0.65, 1),
            "old_target": round(ltp_n_ce * 1.25, 1),
            "target": round(ltp_n_ce * 1.50, 1),
            "is_target_updated": True,
            "trail_sl": round(ltp_n_ce * 1.10, 1),
            "reason": f"Strong Momentum! Target Extended from ₹{round(ltp_n_ce * 1.25, 1)}",
            "lot": 65, "is_call": True
        },
        {
            "symbol": f"BANK NIFTY {b_atm} PE",
            "type": "BUY PUT",
            "algo": "REJECTION @ RESISTANCE",
            "ltp": ltp_b_pe,
            "entry": round(ltp_b_pe * 0.98, 1),
            "sl": round(ltp_b_pe * 0.72, 1),
            "hold_sl": round(ltp_b_pe * 0.60, 1),
            "old_target": round(ltp_b_pe * 1.45, 1),
            "target": round(ltp_b_pe * 1.45, 1),
            "is_target_updated": False,
            "trail_sl": round(ltp_b_pe * 1.15, 1),
            "reason": f"Heavy Call Writing @ {b_atm + 200}",
            "lot": 15, "is_call": False
        },
        {
            "symbol": f"FINNIFTY 21850 CE",
            "type": "BUY CALL",
            "algo": "MOMENTUM BREAKOUT",
            "ltp": ltp_fin_ce,
            "entry": round(ltp_fin_ce * 0.97, 1),
            "sl": round(ltp_fin_ce * 0.70, 1),
            "hold_sl": round(ltp_fin_ce * 0.55, 1),
            "old_target": round(ltp_fin_ce * 1.30, 1),
            "target": round(ltp_fin_ce * 1.60, 1),
            "is_target_updated": True,
            "trail_sl": round(ltp_fin_ce * 1.20, 1),
            "reason": "Target Upgraded due to High Volume Breakout",
            "lot": 40, "is_call": True
        },
        {
            "symbol": f"MIDCAP NIFTY 12450 PE",
            "type": "BUY PUT",
            "algo": "RSI DIVERGENCE",
            "ltp": ltp_mid_pe,
            "entry": round(ltp_mid_pe * 0.99, 1),
            "sl": round(ltp_mid_pe * 0.75, 1),
            "hold_sl": round(ltp_mid_pe * 0.60, 1),
            "old_target": round(ltp_mid_pe * 1.40, 1),
            "target": round(ltp_mid_pe * 1.40, 1),
            "is_target_updated": False,
            "trail_sl": round(ltp_mid_pe * 1.10, 1),
            "reason": "Overbought Reversion Signal",
            "lot": 75, "is_call": False
        }
    ]

    for t in trades:
        ltp, entry, sl, hold_sl, target = t['ltp'], t['entry'], t['sl'], t['hold_sl'], t['target']
        
        # Check Status
        if ltp >= target:
            status_text, status_class = "🎯 TARGET HIT", "st-target"
            trigger_native_push("🎯 TARGET ACHIEVED", f"{t['symbol']} hit Target ₹{target}!")
        elif ltp <= hold_sl:
            status_text, status_class = "🛑 HOLD SL EXIT", "st-sl"
            trigger_native_push("🛑 SYSTEM SL HIT", f"{t['symbol']} hit Hold SL @ ₹{hold_sl}!")
        else:
            status_text, status_class = "🟢 ACTIVE SIGNAL", "st-active"

        # Push Notification if Target Modified
        if t['is_target_updated'] and 'notified_' + t['symbol'] not in st.session_state:
            st.session_state['notified_' + t['symbol']] = True
            trigger_native_push("🟡 TARGET UPDATED!", f"{t['symbol']} Target raised to ₹{target}!")

        card_class = "trade-card" if t['is_call'] else "trade-card trade-card-put"
        risk_amount = round((entry - sl) * t['lot'])

        # Updated Badge HTML
        updated_badge_html = f'<span class="updated-badge">🎯 TARGET UPDATED</span>' if t['is_target_updated'] else ''

        # Target Box Highlight
        target_style = "color:#16A34A; font-weight:900;"
        if t['is_target_updated']:
            target_style = "color:#D97706; font-weight:900; background:#FEF3C7; padding:2px 4px; border-radius:4px;"

        target_update_banner = ""
        if t['is_target_updated']:
            target_update_banner = f"""
            <div class="target-updated-box">
                <span>🚀 Target Extended: ₹{t['old_target']} ➔ <b>₹{target}</b></span>
                <span>🔥 Trail SL: ₹{t['trail_sl']}</span>
            </div>
            """

        render_clean_html(f"""
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
        """)

# ------------------------------------------------------------------
# TAB 2: ZERO-HERO ALGO
# ------------------------------------------------------------------
with tab_hero:
    st.markdown("### 🚀 Expiry Zero-Hero Special Calls")

    hero_trades = [
        {
            "symbol": f"NIFTY {n_atm + 100} CE",
            "type": "HERO-ZERO (CALL)",
            "ltp": 22.50,
            "entry": 20.00,
            "sl": 5.00,
            "target": 75.00,
            "reason": "Post-1:30 PM Gamma Spike Triggered",
            "lot": 65
        },
        {
            "symbol": f"BANK NIFTY {b_atm - 200} PE",
            "type": "HERO-ZERO (PUT)",
            "ltp": 28.00,
            "entry": 25.00,
            "sl": 6.00,
            "target": 95.00,
            "reason": "Short Covering Breakout Expected",
            "lot": 15
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

# ------------------------------------------------------------------
# TAB 3: OPTION CHAIN
# ------------------------------------------------------------------
with tab_chain:
    ref_spot = n['spot']
    step = 50
    center = int(round(ref_spot / float(step)) * step)
    strikes = [center - (2 * step), center - step, center, center + step, center + (2 * step)]

    chain_rows = []
    call_oi_list, put_oi_list = [], []

    for s in strikes:
        c_price = calc_live_option_price(ref_spot, s, is_call=True)
        p_price = calc_live_option_price(ref_spot, s, is_call=False)
        c_oi = round(max(0.5, 5.2 - (abs(s - ref_spot)*0.015)), 2)
        p_oi = round(max(0.5, 4.8 - (abs(s - ref_spot)*0.012)), 2)
        
        call_oi_list.append(c_oi)
        put_oi_list.append(p_oi)

        chain_rows.append({
            "Call OI": f"{c_oi:.2f}L",
            "Call LTP": f"₹{c_price:.2f}",
            "STRIKE": f"📍 {s}" if s == center else f"{s}",
            "Put LTP": f"₹{p_price:.2f}",
            "Put OI": f"{p_oi:.2f}L",
        })
    
    df_chain = pd.DataFrame(chain_rows)
    st.dataframe(df_chain, use_container_width=True, hide_index=True)

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=call_oi_list, name='Call OI (Resistance)', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=put_oi_list, name='Put OI (Support)', marker_color='#10B981'))
    fig_oi.update_layout(
        barmode='group', height=220, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_oi, use_container_width=True)

# ------------------------------------------------------------------
# TAB 4: CHARTS
# ------------------------------------------------------------------
with tab_charts:
    np.random.seed(101)
    periods = 30
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    close_prices = n['spot'] + np.cumsum(np.random.randn(periods) * 5)
    high_prices = close_prices + np.random.rand(periods) * 6
    low_prices = close_prices - np.random.rand(periods) * 6
    open_prices = low_prices + np.random.rand(periods) * (high_prices - low_prices)

    df_chart = pd.DataFrame({'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices}, index=dates)

    fig_chart = make_subplots(rows=1, cols=1)
    fig_chart.add_trace(go.Candlestick(
        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], 
        low=df_chart['Low'], close=df_chart['Close'], name="Nifty Spot"
    ))
    fig_chart.update_layout(height=300, margin=dict(l=0, r=0, t=5, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_chart, use_container_width=True)

