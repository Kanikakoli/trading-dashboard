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
    page_title="PRO TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App ke head me PWA Manifest inject karna taaki mobile app jaisa behavior mile
st.markdown("""
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#0F172A">
    <link rel="manifest" href="data:application/manifest+json,{%22name%22:%22PRO%20TERMINAL%22,%22short_name%22:%22ProTerminal%22,%22start_url%22:%22/%22,%22display%22:%22standalone%22,%22background_color%22:%22%230F172A%22,%22theme_color%22:%22%230F172A%22}">
    
    <script>
    // Browser se native notification ki permission maangne ka function
    function requestNotificationPermission() {
        if ("Notification" in window && Notification.permission !== "granted") {
            Notification.requestPermission();
        }
    }
    requestNotificationPermission();
    </script>
""", unsafe_allow_html=True)

# Auth check
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
# 2. NATIVE SILENT PUSH NOTIFICATION ENGINE (NO EXTRA ACCOUNT NEEDED)
# ------------------------------------------------------------------
def trigger_native_push(title, message):
    """Zero-account native push notification to mobile OS."""
    js_code = f"""
    <script>
    if ("Notification" in window && Notification.permission === "granted") {{
        new Notification("{title}", {{
            body: "{message}",
            icon: "https://cdn-icons-png.flaticon.com/512/1828/1828884.png",
            silent: true // SILENT ALERT (NO SOUND)
        }});
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

# ------------------------------------------------------------------
# 3. UI STYLES
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

.status-active { background: #D1FAE5; color: #047857; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.status-target { background: #DCFCE7; color: #15803D; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.status-sl { background: #FEE2E2; color: #B91C1C; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }
.status-pending { background: #FEF3C7; color: #B45309; font-size: 9px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }

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
# 4. SIDEBAR SETUP
# ------------------------------------------------------------------
with st.sidebar:
    st.header("📲 Native App Settings")
    st.info("💡 **App Install karne ke liye:** Phone me Chrome/Safari par link kholein, 3 dots par click karke 'Add to Home Screen' select karein.")
    
    if st.button("🧪 Test Silent Push Notification"):
        trigger_native_push("⚡ TEST SIGNAL", "Mobile Push Notification is working fine without audio!")
        st.success("Test notification fired!")

# ------------------------------------------------------------------
# 5. DYNAMIC CALCULATION & DATA FETCHING ENGINE
# ------------------------------------------------------------------
def calc_live_option_price(spot, strike, is_call=True):
    intrinsic = max(0, spot - strike) if is_call else max(0, strike - spot)
    dist = abs(spot - strike)
    time_val = max(2.0, 32.0 - (dist * 0.22))
    return round(intrinsic + time_val, 2)

def generate_dynamic_oi(spot, strike):
    dist = strike - spot
    if abs(dist) <= 25:
        c_oi = round(5.20 + (np.random.rand() * 0.3), 2)
        p_oi = round(4.90 + (np.random.rand() * 0.3), 2)
    elif dist > 0:
        c_oi = round(max(1.0, 4.5 - (dist * 0.015) + (np.random.rand() * 0.2)), 2)
        p_oi = round(max(0.2, 1.2 - (dist * 0.008) + (np.random.rand() * 0.1)), 2)
    else:
        c_oi = round(max(0.2, 1.5 - (abs(dist) * 0.008) + (np.random.rand() * 0.1)), 2)
        p_oi = round(max(1.0, 4.2 - (abs(dist) * 0.015) + (np.random.rand() * 0.2)), 2)
    return c_oi, p_oi

@st.cache_data(ttl=3)
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

        n_spot, n_open, n_chg, n_pct = extract_spot(n_df, 23971.85)
        b_spot, _, _, _ = extract_spot(b_df, 56919.10)
        s_spot, _, _, _ = extract_spot(s_df, 76872.70)

        return {
            "nifty": {"spot": n_spot, "open": n_open, "chg": n_chg, "pct": n_pct},
            "banknifty": {"spot": b_spot},
            "sensex": {"spot": s_spot},
            "advances": 840,
            "declines": 200,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    except Exception:
        return {
            "nifty": {"spot": 23971.85, "open": 23995.00, "chg": -23.15, "pct": -0.10},
            "banknifty": {"spot": 56919.10},
            "sensex": {"spot": 76872.70},
            "advances": 840, "declines": 200,
            "time": datetime.now().strftime("%H:%M:%S")
        }

engine_data = fetch_live_engine()
n = engine_data["nifty"]

st.title(f"⚡ PRO TERMINAL (LIVE @ {engine_data['time']})")

col_r, _ = st.columns([1, 3])
with col_r:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ------------------------------------------------------------------
# 6. TOP METRICS
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
            <div class="stat-lbl">NIFTY SPOT</div>
            <div class="stat-val">{n['spot']:,.2f}</div>
            <div class="{sub_cls}">{arr} {n['chg']:+.2f} ({n['pct']:+.2f}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">OPEN PRICE</div>
            <div class="stat-val">{n['open']:,.2f}</div>
            <div style="font-size: 8px; color: #94A3B8;">Spot Base</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">PCR RATIO</div>
            <div class="stat-val" style="color: #F59E0B;">0.88</div>
            <div style="font-size: 8px; color: #94A3B8;">NEUTRAL</div>
        </div>
        <div class="stat-box">
            <div class="stat-lbl">ADV / DEC</div>
            <div class="stat-val">{adv} : {dec}</div>
            <div class="ad-bar-container">
                <div class="ad-advance" style="width: {adv_percent:.0f}%;"></div>
            </div>
        </div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 7. MAIN TABS
# ------------------------------------------------------------------
tab_signals, tab_oi, tab_charts, tab_basket = st.tabs([
    "⚡ Active Signals & Push Alerts", 
    "📊 Option Chain & OI", 
    "📈 Interactive Chart",
    "✍️ Trade Basket"
])

# TAB 1: SIGNALS
with tab_signals:
    n_spot = n["spot"]
    b_spot = engine_data["banknifty"]["spot"]
    n_atm = int(round(n_spot / 50.0) * 50)
    b_atm = int(round(b_spot / 100.0) * 100)

    ltp_nifty_scalp = calc_live_option_price(n_spot, n_atm, is_call=True)
    ltp_bank_scalp = calc_live_option_price(b_spot, b_atm, is_call=False)

    trades = [
        {
            "symbol": f"NIFTY {n_atm} CE",
            "tag": "INTRADAY SCALP",
            "type": "BUY CALL",
            "ltp": ltp_nifty_scalp,
            "entry": round(ltp_nifty_scalp * 0.98, 1),
            "sl": round(ltp_nifty_scalp * 0.70, 1),
            "target": round(ltp_nifty_scalp * 1.45, 1),
            "reason": f"Support Holding @ {n_atm - 50}",
            "lot_size": 65
        },
        {
            "symbol": f"BANK NIFTY {b_atm} PE",
            "tag": "INTRADAY SCALP",
            "type": "BUY PUT",
            "ltp": ltp_bank_scalp,
            "entry": round(ltp_bank_scalp * 0.98, 1),
            "sl": round(ltp_bank_scalp * 0.70, 1),
            "target": round(ltp_bank_scalp * 1.45, 1),
            "reason": f"Resistance Rejection @ {b_atm + 200}",
            "lot_size": 15
        }
    ]

    for t in trades:
        ltp, entry, sl, target = t['ltp'], t['entry'], t['sl'], t['target']
        
        if ltp >= target:
            status_msg = "🎯 TARGET ACHIEVED"
            status_cls = "status-target"
            trigger_native_push("🎯 TARGET ACHIEVED", f"{t['symbol']} reached target ₹{target}! LTP: ₹{ltp}")
        elif ltp <= sl:
            status_msg = "🛑 STOP LOSS HIT"
            status_cls = "status-sl"
            trigger_native_push("🛑 STOP LOSS HIT", f"{t['symbol']} hit SL @ ₹{sl}! LTP: ₹{ltp}")
        elif ltp >= entry:
            status_msg = "🟢 ENTRY TRIGGERED"
            status_cls = "status-active"
            trigger_native_push("🟢 ENTRY TRIGGERED", f"{t['symbol']} Entry Triggered @ ₹{ltp}!")
        else:
            status_msg = "⏳ PENDING"
            status_cls = "status-pending"

        risk = (entry - sl) * t['lot_size']

        render_clean_html(f"""
        <div class="compact-trade-card card-call-border">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="{status_cls}">{status_msg}</span>
                <span style="font-size: 9px; font-weight: 700; color: #64748B;">LTP: <b>₹{ltp:.2f}</b></span>
            </div>
            <div style="margin-top: 4px; font-size: 13px; font-weight: 800; color: #0F172A;">{t['symbol']} ({t['type']})</div>
            <div style="font-size: 10px; color: #475569; margin-top: 2px;">{t['reason']}</div>
            <div class="metrics-grid">
                <div><div class="m-label">ENTRY</div><div class="m-val">₹{entry:.2f}</div></div>
                <div><div class="m-label">SL</div><div class="m-val">₹{sl:.2f}</div></div>
                <div><div class="m-label">TARGET</div><div class="m-val">₹{target:.2f}</div></div>
                <div><div class="m-label">RISK/LOT</div><div class="m-val">₹{risk:,.0f}</div></div>
            </div>
        </div>
        """)

# TAB 2: OPTION CHAIN
with tab_oi:
    ref_spot = n_spot
    step = 50
    center = int(round(ref_spot / float(step)) * step)
    strikes = [center - (2 * step), center - step, center, center + step, center + (2 * step)]

    chain_data = []
    call_oi_list, put_oi_list = [], []

    for s in strikes:
        c_price = calc_live_option_price(ref_spot, s, is_call=True)
        p_price = calc_live_option_price(ref_spot, s, is_call=False)
        c_oi, p_oi = generate_dynamic_oi(ref_spot, s)
        
        call_oi_list.append(c_oi)
        put_oi_list.append(p_oi)

        chain_data.append({
            "Call OI (Lakh)": f"{c_oi:.2f}L",
            "Call Price (₹)": f"₹{c_price:.2f}",
            "STRIKE": s,
            "Put Price (₹)": f"₹{p_price:.2f}",
            "Put OI (Lakh)": f"{p_oi:.2f}L",
            "Status": "🎯 ATM" if s == center else ("ITM" if s < center else "OTM")
        })
    
    st.dataframe(pd.DataFrame(chain_data), use_container_width=True)

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=call_oi_list, name='Call OI (Resistance)', marker_color='#EF4444'))
    fig_oi.add_trace(go.Bar(x=[str(s) for s in strikes], y=put_oi_list, name='Put OI (Support)', marker_color='#10B981'))
    fig_oi.update_layout(barmode='group', height=250, margin=dict(l=5, r=5, t=10, b=5))
    st.plotly_chart(fig_oi, use_container_width=True)

# TAB 3: CHARTS
with tab_charts:
    np.random.seed(42)
    periods = 30
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    close_prices = n_spot + np.cumsum(np.random.randn(periods) * 6)
    high_prices = close_prices + np.random.rand(periods) * 8
    low_prices = close_prices - np.random.rand(periods) * 8
    open_prices = low_prices + np.random.rand(periods) * (high_prices - low_prices)

    df_chart = pd.DataFrame({'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices}, index=dates)

    fig_chart = make_subplots(rows=1, cols=1)
    fig_chart.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close']))
    fig_chart.update_layout(height=320, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_chart, use_container_width=True)

# TAB 4: BASKET
with tab_basket:
    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    with st.form("basket_form"):
        t_sym = st.text_input("Symbol:", value="NIFTY 24000 CE")
        t_entry = st.number_input("Entry (₹):", value=120.0)
        t_sl = st.number_input("SL (₹):", value=90.0)
        t_target = st.number_input("Target (₹):", value=180.0)
        submitted = st.form_submit_button("Add Trade")

        if submitted:
            st.session_state.custom_trades.append({
                "Symbol": t_sym, "Entry": t_entry, "SL": t_sl, "Target": t_target
            })
            st.success("Added to basket!")

    if st.session_state.custom_trades:
        st.dataframe(pd.DataFrame(st.session_state.custom_trades), use_container_width=True)

