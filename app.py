import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE CONFIGURATION (Mobile Responsive Layout)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Mobile
st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        .metric-box {
            background-color: #1E222D;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #2B2E3A;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PASSCODE SECURITY
# ---------------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("## 🔒 Private Trading Terminal")
        st.caption("Enter your passcode to access the terminal.")
        
        passcode = st.text_input("Passcode", type="password", key="pwd_input")
        if st.button("Unlock Terminal", use_container_width=True):
            if passcode == "1234":  # Change your default passcode here
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect passcode. Try again.")
        return False
    return True

if not check_password():
    st.stop()

# ---------------------------------------------------------
# TERMINAL HEADER & NAVIGATION
# ---------------------------------------------------------
st.title("⚡ Pro Terminal")

index_choice = st.selectbox("Select Index", ["NIFTY 50", "BANK NIFTY", "FINNIFTY"])

# Default Index Configurations
index_configs = {
    "NIFTY 50": {"spot": 24500, "step": 50, "lot_size": 65},
    "BANK NIFTY": {"spot": 52200, "step": 100, "lot_size": 30},
    "FINNIFTY": {"spot": 23100, "step": 50, "lot_size": 60}
}

config = index_configs[index_choice]
spot_price = config["spot"]

# Top Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-box'><b>Spot</b><br><h3>{spot_price}</h3></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><b>Lot Size</b><br><h3>{config['lot_size']}</h3></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-box'><b>PCR</b><br><h3>1.12</h3></div>", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# TABS FOR TOOLS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Option Chain", "🧮 Calculator", "📈 Chart"])

# TAB 1: OPTION CHAIN ANALYSIS
with tab1:
    st.subheader("Strike Matrix")
    
    strikes = [spot_price + (i * config["step"]) for i in range(-5, 6)]
    
    np.random.seed(42)
    ce_oi = np.random.randint(10000, 80000, size=len(strikes))
    pe_oi = np.random.randint(10000, 80000, size=len(strikes))
    ce_ltp = np.round(np.linspace(250, 10, len(strikes)), 2)
    pe_ltp = np.round(np.linspace(10, 250, len(strikes)), 2)
    
    df_chain = pd.DataFrame({
        "CE OI": ce_oi,
        "CE Price": ce_ltp,
        "Strike": strikes,
        "PE Price": pe_ltp,
        "PE OI": pe_oi
    })
    
    st.dataframe(df_chain, use_container_width=True, hide_index=True)

# TAB 2: POSITION SIZING & RISK CALCULATOR
with tab2:
    st.subheader("Position Sizing & Risk")
    
    entry_price = st.number_input("Entry Premium Price", value=150.0, step=5.0)
    stop_loss = st.number_input("Stop Loss Price", value=120.0, step=5.0)
    lots = st.number_input("Number of Lots", value=2, step=1)
    
    total_qty = lots * config["lot_size"]
    total_capital = entry_price * total_qty
    risk_per_trade = (entry_price - stop_loss) * total_qty
    
    st.write(f"**Total Quantity:** {total_qty} units")
    st.write(f"**Capital Required:** ₹{total_capital:,.2f}")
    st.write(f"**Max Loss (Risk):** ₹{risk_per_trade:,.2f}")

# TAB 3: PRICE ACTION VISUALIZER
with tab3:
    st.subheader("Price Movement")
    
    # Generate Mock Candlestick Data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=20, freq="15min")
    open_p = spot_price + np.random.randn(20) * 20
    high_p = open_p + np.random.rand(20) * 15
    low_p = open_p - np.random.rand(20) * 15
    close_p = open_p + np.random.randn(20) * 10
    
    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open_p, high=high_p,
        low=low_p, close=close_p,
        increasing_line_color='#00E676', 
        decreasing_line_color='#FF5252'
    )])
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
if st.button("🔒 Lock Terminal", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()
