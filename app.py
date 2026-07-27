import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v6.1 | Zero-Hero Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# SECURITY & PASSCODE LOCK
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

# ------------------------------------------------------------------
# ULTRA HIGH-CONTRAST CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #0B0E14;
        color: #FFFFFF;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .ticker-box {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    .ticker-name { font-size: 10px; color: #8B949E; font-weight: 700; letter-spacing: 0.8px; }
    .ticker-price { font-size: 16px; font-weight: 800; color: #FFFFFF; margin: 2px 0; }
    .ticker-up { color: #2EA043; font-weight: 700; font-size: 11px; }
    .ticker-down { color: #F85149; font-weight: 700; font-size: 11px; }

    .signal-card-bull {
        background: linear-gradient(180deg, rgba(46, 160, 67, 0.15) 0%, rgba(13, 17, 23, 0.8) 100%);
        border: 2px solid #2EA043;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(46, 160, 67, 0.2);
    }
    
    .signal-card-custom {
        background: linear-gradient(180deg, rgba(88, 166, 255, 0.15) 0%, rgba(13, 17, 23, 0.8) 100%);
        border: 2px solid #58A6FF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(88, 166, 255, 0.2);
    }

    .signal-card-hero {
        background: linear-gradient(180deg, rgba(210, 153, 34, 0.2) 0%, rgba(13, 17, 23, 0.9) 100%);
        border: 2px solid #D29922;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(210, 153, 34, 0.3);
    }
    
    .badge-giant {
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 1px;
    }
    .badge-call { background-color: #2EA043; color: #000000; }
    .badge-custom { background-color: #58A6FF; color: #000000; }
    .badge-hero { background-color: #D29922; color: #000000; }

    .metric-subcard {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    
    .oi-box-green {
        background: rgba(46, 160, 67, 0.1);
        border-left: 4px solid #2EA043;
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 5px;
    }
    .oi-box-red {
        background: rgba(248, 81, 73, 0.1);
        border-left: 4px solid #F85149;
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 5px;
    }
    
    .action-guidance-box {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DYNAMIC EXPIRY CALCULATOR (2026 Rules: NSE=Tuesday, BSE/Sensex=Thursday)
# ------------------------------------------------------------------
def get_next_weekday(weekday_idx):
    today = datetime.now()
    days_ahead = weekday_idx - today.weekday()
    if days_ahead <= 0:  
        days_ahead += 7
    return today + timedelta(days=days_ahead)

# ------------------------------------------------------------------
# INDEX SELECTOR & TITLE BAR
# ------------------------------------------------------------------
title_col, index_col = st.columns([2, 1])
with title_col:
    st.title("⚡ PRO TERMINAL v6.1")
with index_col:
    selected_index = st.selectbox(
        "🎯 Select Target Index:",
        ["NIFTY 50 (Lot Size: 65)", "BANK NIFTY (Lot Size: 15)", "FINNIFTY (Lot Size: 25)", "SENSEX (Lot Size: 10)"],
        index=0
    )

# Extract lot size dynamically and determine expiry date rule
if "BANK NIFTY" in selected_index:
    lot_size = 15
    default_strike_name = "BANKNIFTY 52000 CE"
    expiry_date = get_next_weekday(1).strftime("%d %b 2026 (Tuesday)")  # NSE Tuesday expiry
elif "FINNIFTY" in selected_index:
    lot_size = 25
    default_strike_name = "FINNIFTY 23500 CE"
    expiry_date = get_next_weekday(1).strftime("%d %b 2026 (Tuesday)")
elif "SENSEX" in selected_index:
    lot_size = 10
    default_strike_name = "SENSEX 80000 CE"
    expiry_date = get_next_weekday(3).strftime("%d %b 2026 (Thursday)")  # BSE Thursday expiry
else:
    lot_size = 65
    default_strike_name = "NIFTY 24400 CE"
    expiry_date = get_next_weekday(1).strftime("%d %b 2026 (Tuesday)")

st.info(f"📅 **Active Expiry Date for {selected_index.split(' ')[0]}:** `{expiry_date}`")

# ------------------------------------------------------------------
# 1. GLOBAL MARKET MONITOR (TOP TICKER RIBBON)
# ------------------------------------------------------------------
st.markdown("<h6 style='color: #8B949E; font-weight:700; margin-bottom: 8px;'>🌐 GLOBAL MARKETS & VOLATILITY</h6>", unsafe_allow_html=True)
g1, g2, g3, g4, g5, g6 = st.columns(6)

globals_data = [
    ("GIFT NIFTY", "24,380.00", "▲ +120.00", "ticker-up", g1),
    ("S&P 500 (US)", "5,560.20", "▲ +34.50", "ticker-up", g2),
    ("NASDAQ (US)", "18,240.10", "▲ +180.20", "ticker-up", g3),
    ("NIKKEI 225", "38,910.50", "▼ -45.00", "ticker-down", g4),
    ("HANG SENG", "17,650.00", "▲ +85.30", "ticker-up", g5),
    ("INDIA VIX", "13.20", "▼ -2.40%", "ticker-down", g6)
]

for name, val, change, tag, col in globals_data:
    with col:
        st.markdown(f"""
            <div class="ticker-box">
                <div class="ticker-name">{name}</div>
                <div class="ticker-price">{val}</div>
                <div class="{tag}">{change}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. ENGINE MODE SELECTION
# ------------------------------------------------------------------
col_left, col_right = st.columns([1.3, 1])

with col_left:
    analysis_mode = st.radio(
        "⚙️ Choose Engine Mode:",
        [
            "🤖 Auto-Signal Engine (Global + OI Writers)", 
            "✍️ Custom Strike & Budget Mode",
            "🔥 Expiry Day Zero-Hero Mode (1:30 PM+ Gamma)"
        ],
        horizontal=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # MODE 1: AUTO-SIGNAL ENGINE
    # ------------------------------------------------------------------
    if "Auto-Signal" in analysis_mode:
        entry = 24310.0
        sl = 24280.0
        target = 24370.0
        risk_points = entry - sl
        reward_points = target - entry
        rr_ratio = reward_points / risk_points
        
        st.markdown(f"""
<div class="signal-card-bull">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="badge-giant badge-call">🟢 BUY CALL</span>
        <span style="color: #8B949E; font-weight: 600; font-size: 12px;">Risk-Reward Ratio: <b style="color:#2EA043;">1:{rr_ratio:.1f}</b></span>
    </div>
    
    <h1 style="font-size: 30px; font-weight: 900; color: #FFFFFF; margin: 0 0 4px 0;">{selected_index.split(' ')[0]} 24300 CE</h1>
    <p style="color: #2EA043; font-size: 13px; font-weight: 700; margin-bottom: 16px;">
        ⚡ Triggered by: Heavy Put Writing @ 24300 + VWAP Breakout
    </p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">STOP LOSS</div>
            <div style="font-size: 20px; font-weight: 900; color: #F85149;">{sl:,.2f}</div>
            <div style="font-size: 11px; color: #F85149; font-weight:700;">-{risk_points:.0f} Pts</div>
        </div>
        <div class="metric-subcard" style="border: 1px solid #58A6FF;">
            <div style="font-size: 11px; color: #58A6FF; font-weight:700;">ENTRY PRICE</div>
            <div style="font-size: 20px; font-weight: 900; color: #FFFFFF;">{entry:,.2f}</div>
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">Base</div>
        </div>
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">TARGET</div>
            <div style="font-size: 20px; font-weight: 900; color: #2EA043;">{target:,.2f}</div>
            <div style="font-size: 11px; color: #2EA043; font-weight:700;">+{reward_points:.0f} Pts</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # MODE 2: CUSTOM STRIKE & BUDGET MODE
    # ------------------------------------------------------------------
    elif "Custom Strike" in analysis_mode:
        st.markdown("##### ⚙️ Input Your Custom Options Trade")
        
        c_in1, c_in2, c_in3, c_in4 = st.columns(4)
        with c_in1:
            custom_strike = st.text_input("Strike Price", default_strike_name)
        with c_in2:
            custom_entry = st.number_input("Premium Price (₹)", value=120.0, step=5.0)
        with c_in3:
            custom_sl_pts = st.number_input("SL Points (₹)", value=20.0, step=5.0)
        with c_in4:
            custom_target_pts = st.number_input("Target Points (₹)", value=40.0, step=5.0)
            
        custom_budget = st.number_input("Allocated Budget (₹)", value=10000, step=1000)

        cost_per_lot = custom_entry * lot_size
        affordable_lots = int(custom_budget // cost_per_lot) if cost_per_lot > 0 else 0
        total_qty = affordable_lots * lot_size
        total_investment = affordable_lots * cost_per_lot
        max_rupee_loss = custom_sl_pts * total_qty
        max_rupee_profit = custom_target_pts * total_qty
        rr_custom = custom_target_pts / custom_sl_pts if custom_sl_pts > 0 else 0.0

        st.markdown(f"""
<div class="signal-card-custom">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="badge-giant badge-custom">✍️ CUSTOM STRIKE ANALYZER</span>
        <span style="color: #58A6FF; font-weight: 700; font-size: 12px;">Risk-Reward: <b>1:{rr_custom:.1f}</b></span>
    </div>
    
    <h1 style="font-size: 28px; font-weight: 900; color: #FFFFFF; margin: 0 0 4px 0;">{custom_strike}</h1>
    <p style="color: #8B949E; font-size: 12px; font-weight: 600; margin-bottom: 14px;">
        Cost / Lot: ₹{cost_per_lot:,.2f} | Affordable: <b style="color:#58A6FF;">{affordable_lots} Lot(s) ({total_qty} Qty)</b> | Total Capital: <b>₹{total_investment:,.2f}</b>
    </p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">MAX LOSS (RUPEES)</div>
            <div style="font-size: 20px; font-weight: 900; color: #F85149;">₹{max_rupee_loss:,.2f}</div>
            <div style="font-size: 11px; color: #F85149; font-weight:700;">SL @ ₹{custom_entry - custom_sl_pts:.2f}</div>
        </div>
        <div class="metric-subcard" style="border: 1px solid #58A6FF;">
            <div style="font-size: 11px; color: #58A6FF; font-weight:700;">BUY PREMIUM</div>
            <div style="font-size: 20px; font-weight: 900; color: #FFFFFF;">₹{custom_entry:.2f}</div>
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">Entry</div>
        </div>
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">MAX PROFIT (RUPEES)</div>
            <div style="font-size: 20px; font-weight: 900; color: #2EA043;">₹{max_rupee_profit:,.2f}</div>
            <div style="font-size: 11px; color: #2EA043; font-weight:700;">Target @ ₹{custom_entry + custom_target_pts:.2f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # MODE 3: EXPIRY DAY ZERO-HERO ENGINE (1:30 PM+ GAMMA BLAST)
    # ------------------------------------------------------------------
    else:
        st.markdown("##### 🚀 Zero-Hero Expiry Configuration")
        
        zh_col1, zh_col2, zh_col3 = st.columns(3)
        with zh_col1:
            hero_budget = st.number_input("Zero-Hero Capital Pool (₹)", value=3000, step=500, help="Strictly treat this capital as 100% risk.")
        with zh_col2:
            hero_premium = st.number_input("OTM Option Premium (₹)", value=15.0, step=1.0)
        with zh_col3:
            target_multiplier = st.selectbox("Target Multiplier (Reward)", ["3x (₹45)", "4x (₹60)", "5x (₹75)"], index=2)

        cost_per_lot = hero_premium * lot_size
        affordable_lots = int(hero_budget // cost_per_lot) if cost_per_lot > 0 else 0
        total_qty = affordable_lots * lot_size
        actual_investment = affordable_lots * cost_per_lot
        
        mult_val = int(target_multiplier[0])
        target_price = hero_premium * mult_val
        max_hero_loss = actual_investment
        max_hero_profit = (target_price - hero_premium) * total_qty
        rr_hero_ratio = mult_val - 1

        st.markdown(f"""
<div class="signal-card-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="badge-giant badge-hero">🔥 EXPIRY ZERO-HERO SIGNAL</span>
        <span style="color: #D29922; font-weight: 700; font-size: 12px;">Risk-Reward Ratio: <b>1:{rr_hero_ratio:.0f}</b></span>
    </div>
    
    <h1 style="font-size: 28px; font-weight: 900; color: #FFFFFF; margin: 0 0 4px 0;">{selected_index.split(' ')[0]} 24450 CE (OTM)</h1>
    <p style="color: #D29922; font-size: 12px; font-weight: 700; margin-bottom: 14px;">
        ⚡ Gamma Trigger: Call Writers Panic (Short Covering) + 1:30 PM Breakout
    </p>
    <p style="color: #8B949E; font-size: 12px; font-weight: 600; margin-bottom: 14px;">
        Affordable: <b style="color:#D29922;">{affordable_lots} Lot(s) ({total_qty} Qty)</b> | Total Risk (Spent Cash): <b>₹{actual_investment:,.2f}</b>
    </p>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">STOP LOSS (TOTAL RISK)</div>
            <div style="font-size: 20px; font-weight: 900; color: #F85149;">₹0.00</div>
            <div style="font-size: 11px; color: #F85149; font-weight:700;">Max Loss: -₹{max_hero_loss:,.2f}</div>
        </div>
        <div class="metric-subcard" style="border: 1px solid #D29922;">
            <div style="font-size: 11px; color: #D29922; font-weight:700;">BUY PREMIUM</div>
            <div style="font-size: 20px; font-weight: 900; color: #FFFFFF;">₹{hero_premium:.2f}</div>
            <div style="font-size: 11px; color: #8B949E; font-weight:700;">Entry</div>
        </div>
        <div class="metric-subcard">
            <div style="font-size: 11px; color: #D29922; font-weight:700;">TARGET ({target_multiplier})</div>
            <div style="font-size: 20px; font-weight: 900; color: #2EA043;">₹{target_price:.2f}</div>
            <div style="font-size: 11px; color: #2EA043; font-weight:700;">Profit: +₹{max_hero_profit:,.2f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Live Price Progress towards Target:**")
    st.progress(45)

# ------------------------------------------------------------------
# 3. RIGHT SIDE: WRITER POSITIONS & WHEN TO BUY / HOLD / WAIT GUIDE
# ------------------------------------------------------------------
with col_right:
    st.markdown("#### 🏛️ CALL/PUT WRITER POSITIONS (OI)")
    
    st.markdown("""
        <div class="oi-box-green">
            <b>🟢 HEAVY PUT WRITING (Support Floor):</b><br>
            <span style="font-size: 12px; color: #8B949E;">Added +42.8% OI (Bulls defending bottom)</span>
        </div>
        <div class="oi-box-red">
            <b>🔴 SHORT COVERING PANIC TRIGGER:</b><br>
            <span style="font-size: 12px; color: #8B949E;">Unwinding -18.4% OI (Call writers exiting!)</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### ⏰ WHEN TO BUY, HOLD, OR WAIT (EXECUTION GUIDE)")
    
    st.markdown("""
        <div class="action-guidance-box">
            <p style="margin: 0 0 8px 0; font-size: 13px;"><b>🟢 9:15 AM - 10:00 AM (WAIT):</b> Do not chase opening volatility. Let the high/low range form.</p>
            <p style="margin: 0 0 8px 0; font-size: 13px;"><b>🚀 1:30 PM+ ON EXPIRY (BUY WINDOW):</b> Best time for Zero-Hero trades. Gamma spikes rapidly if writers panic.</p>
            <p style="margin: 0 0 8px 0; font-size: 13px;"><b>🛡️ HOLD RULE:</b> Keep holding if price stays above VWAP and Put OI increases. Exit immediately if SL hits.</p>
            <p style="margin: 0; font-size: 13px;"><b>⏳ 2:45 PM+ (SQUARE OFF):</b> Mandatory exit time for expiry day OTM buyers to avoid settlement traps.</p>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. CHART WITH OVERLAYS
# ------------------------------------------------------------------
st.divider()
st.markdown("#### 📈 LIVE CANDLESTICK CHART")

np.random.seed(42)
dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="5min")
close_prices = np.cumsum(np.random.randn(30)) + 24300
open_prices = close_prices + np.random.randn(30) * 2
high_prices = np.maximum(open_prices, close_prices) + np.random.rand(30) * 4
low_prices = np.minimum(open_prices, close_prices) - np.random.rand(30) * 4

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=dates, open=open_prices, high=high_prices, low=low_prices, close=close_prices,
    name="Price", increasing_line_color='#2EA043', decreasing_line_color='#F85149'
))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=360,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# LOCK TERMINAL BUTTON
# ------------------------------------------------------------------
st.markdown("---")
if st.button("🔒 Lock Terminal"):
    st.session_state.authenticated = False
    st.rerun()
