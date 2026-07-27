import streamlit as st
import pandas as pd
import numpy as np

# Page Config
st.set_page_config(page_title="Pro Trading Terminal", page_icon="📈", layout="wide")

# Custom Dark Theme & Styling
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #238636; color: white; }
    
    /* Custom Badges & Highlight Boxes */
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 8px; text-align: center; }
    .hero-zero-box { background-color: rgba(234, 179, 8, 0.15); border: 1px solid #eab308; padding: 12px; border-radius: 8px; text-align: center; color: #fef08a; font-weight: bold; }
    .bullish { color: #3fb950; font-weight: bold; }
    .bearish { color: #f85149; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. SECURITY & PASSCODE ACCESS
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_passcode():
    if st.session_state.get("passcode_input") == "1234":
        st.session_state.authenticated = True
    else:
        st.error("❌ Invalid Passcode")

if not st.session_state.authenticated:
    st.title("🔐 Terminal Locked")
    st.text_input("Enter Passcode:", type="password", key="passcode_input", on_change=check_passcode)
    st.stop()

# ---------------------------------------------------------
# 2. HEADER & GLOBAL MARKETS FEED
# ---------------------------------------------------------
st.title("⚡ Pro Trading Dashboard")

st.markdown("### 🌐 Global Markets Overview")
g1, g2, g3, g4 = st.columns(4)
g1.markdown('<div class="metric-card"><b>GIFT Nifty</b><br><span class="bullish">+85.50 (+0.35%)</span></div>', unsafe_allow_html=True)
g2.markdown('<div class="metric-card"><b>Dow Jones</b><br><span class="bearish">-120.30 (-0.31%)</span></div>', unsafe_allow_html=True)
g3.markdown('<div class="metric-card"><b>Nasdaq</b><br><span class="bullish">+112.40 (+0.62%)</span></div>', unsafe_allow_html=True)
g4.markdown('<div class="metric-card"><b>India VIX</b><br><span>13.45 (-2.10%)</span></div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 3. NAVIGATION TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Option Chain & Levels", "🚀 Hero Zero Setup", "🧮 Calculator", "📈 Indicators & Charts"])

# --- TAB 1: OPTION CHAIN & S/R LEVELS ---
with tab1:
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.subheader("Option Chain Matrix")
        
        # Matrix Data
        data = {
            "CE OI": [10860, 64886, 16265, 47194, 54131, 70263, 26023, 51090, 77221, 74820],
            "CE Price": [226.0, 202.0, 178.0, 154.0, 130.0, 106.0, 82.0, 58.0, 34.0, 10.0],
            "Strike": [24300, 24350, 24400, 24450, 24500, 24550, 24600, 24650, 24700, 24750],
            "PE Price": [34.0, 58.0, 82.0, 106.0, 130.0, 154.0, 178.0, 202.0, 226.0, 250.0],
            "PE OI": [69735, 72955, 74925, 77969, 15311, 63707, 38693, 35658, 28431, 12747]
        }
        df = pd.DataFrame(data)
        
        st.dataframe(
            df.style.highlight_max(axis=0, color="#1f3a29", subset=["CE OI", "PE OI"]),
            use_container_width=True,
            height=380
        )
        
    with col_right:
        st.subheader("🎯 Key Support & Resistance")
        st.success("🟢 **Resistance 2 (R2):** 24,700")
        st.info("🟢 **Resistance 1 (R1):** 24,550")
        st.warning("🔴 **Support 1 (S1):** 24,450")
        st.error("🔴 **Support 2 (S2):** 24,300")
        
        st.markdown("### PCR Ratio")
        st.metric(label="Put Call Ratio (PCR)", value="1.18", delta="Bullish Bias")

# --- TAB 2: HERO ZERO INDICATOR ---
with tab2:
    st.subheader("🔥 Hero Zero Scanner")
    
    st.markdown("""
    <div class="hero-zero-box">
        <h3>⚡ HERO ZERO TRIGGER ACTIVE</h3>
        <p><b>Target Strike:</b> 24,500 CALL @ ₹15 - ₹20</p>
        <p><b>Condition:</b> Sustaining above R1 (24,550) with heavy PE unwinding.</p>
        <p><b>Target 1:</b> ₹40 | <b>Target 2:</b> ₹65 | <b>SL:</b> ₹5</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 3: CALCULATOR ---
with tab3:
    st.subheader("🧮 Position Size & Risk Calculator")
    c1, c2 = st.columns(2)
    with c1:
        entry = st.number_input("Entry Premium Price", value=100.0)
        target = st.number_input("Target Price", value=130.0)
    with c2:
        stoploss = st.number_input("Stop Loss Price", value=85.0)
        lots = st.number_input("Number of Lots (Lot Size: 25)", value=2, step=1)
        
    total_qty = lots * 25
    profit = (target - entry) * total_qty
    loss = (entry - stoploss) * total_qty
    rr = round((target - entry) / (entry - stoploss), 2) if entry != stoploss else 0
    
    st.info(f"💰 **Total Capital Used:** ₹{entry * total_qty:,.2f}")
    st.success(f"📈 **Max Profit:** ₹{profit:,.2f} | 📉 **Max Loss:** ₹{loss:,.2f} | **Risk-Reward:** 1:{rr}")

# --- TAB 4: INDICATORS & CHART ---
with tab4:
    st.subheader("📈 Technical Indicators & Live Trend")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("RSI (14)", "62.4", "Bullish")
    m2.metric("VWAP", "24,480", "Above VWAP")
    m3.metric("MACD Status", "Bullish Crossover", "+12.4")
    
    st.line_chart(df.set_index("Strike")[["CE Price", "PE Price"]])

# ---------------------------------------------------------
# FOOTER / LOCK BUTTON
# ---------------------------------------------------------
st.markdown("---")
if st.button("🔒 Lock Terminal"):
    st.session_state.authenticated = False
    st.rerun()

