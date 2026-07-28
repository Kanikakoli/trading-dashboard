import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import textwrap

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v8.2 | Visual Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Helper function for rendering HTML safe from indentation errors
def render_html(html_str):
    st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)

# ------------------------------------------------------------------
# STYLING (LIGHT & VIBRANT MODERN UI)
# ------------------------------------------------------------------
render_html("""
<style>
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    
    .card-call {
        background: #FFFFFF;
        border-left: 6px solid #10B981;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    
    .card-put {
        background: #FFFFFF;
        border-left: 6px solid #EF4444;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    
    .metric-pill {
        background: #F1F5F9;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
    }
    
    .badge-bull { background-color: #10B981; color: white; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 12px; }
    .badge-bear { background-color: #EF4444; color: white; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 12px; }
</style>
""")

# ------------------------------------------------------------------
# SIDEBAR CONTROL PANEL
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚡ Terminal Controls")
    selected_index = st.selectbox(
        "🎯 Default Index:",
        ["NIFTY 50", "BANK NIFTY", "FINNIFTY", "SENSEX"]
    )
    
    st.divider()
    st.subheader("💡 Execution Rules")
    st.info("""
    • **09:15 - 09:45:** Wait for Range Breakout  
    • **13:30 Onwards:** Best Zero-Hero Window  
    • **2:45 PM:** Mandatory Intraday Square Off  
    """)
    
    if st.button("🔒 Lock Terminal", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ------------------------------------------------------------------
# HEADER & GLOBAL TICKERS
# ------------------------------------------------------------------
st.title("📊 PRO OPTION TERMINAL v8.2")

# Top Tickers with Streamlit Metrics
t1, t2, t3, t4, t5 = st.columns(5)
t1.metric("GIFT NIFTY", "24,380.0", "+120.0 (+0.5%)")
t2.metric("S&P 500", "5,560.2", "+34.5 (+0.6%)")
t3.metric("NASDAQ", "18,240.1", "+180.2 (+1.0%)")
t4.metric("NIKKEI 225", "38,910.5", "-45.0 (-0.1%)", delta_color="inverse")
t5.metric("INDIA VIX", "13.20", "-0.32 (-2.4%)", delta_color="inverse")

st.divider()

# ------------------------------------------------------------------
# MAIN TABS ARCHITECTURE
# ------------------------------------------------------------------
tab_signals, tab_breadth, tab_portfolio = st.tabs([
    "⚡ Active Trade Signals", 
    "📊 Market Sentiment & Breadth", 
    "✍️ Multi-Trade Portfolio Builder"
])

# ------------------------------------------------------------------
# TAB 1: LIVE SIGNALS WITH VISUAL RISK/REWARD
# ------------------------------------------------------------------
with tab_signals:
    filter_col, search_col = st.columns([1, 2])
    with filter_col:
        filter_index = st.selectbox("Filter Signals By:", ["ALL", "NIFTY 50", "BANK NIFTY", "SENSEX"])

    trades = [
        {
            "symbol": "NIFTY 24300 CE",
            "index": "NIFTY 50",
            "type": "BUY CALL",
            "entry": 110.0, "sl": 90.0, "target": 150.0,
            "reason": "Heavy Put Writing @ 24300 + VWAP Breakout",
            "lot_size": 65
        },
        {
            "symbol": "BANKNIFTY 52200 PE",
            "index": "BANK NIFTY",
            "type": "BUY PUT",
            "entry": 240.0, "sl": 200.0, "target": 320.0,
            "reason": "Call Writing Barrier @ 52500 + Bearish Divergence",
            "lot_size": 15
        },
        {
            "symbol": "SENSEX 80100 CE",
            "index": "SENSEX",
            "type": "BUY CALL",
            "entry": 310.0, "sl": 260.0, "target": 410.0,
            "reason": "Expiry Gamma Squeeze + Short Covering",
            "lot_size": 10
        }
    ]

    filtered_trades = [t for t in trades if filter_index == "ALL" or t["index"] == filter_index]

    for t in filtered_trades:
        risk = t['entry'] - t['sl']
        reward = t['target'] - t['entry']
        rr_ratio = reward / risk if risk > 0 else 0
        is_call = "CALL" in t['type']

        card_class = "card-call" if is_call else "card-put"
        badge_class = "badge-bull" if is_call else "badge-bear"

        with st.container():
            render_html(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span class="{badge_class}">{t['type']}</span>
                    <span style="font-weight: 800; font-size: 13px; color: #475569;">RR Ratio: 1:{rr_ratio:.1f}</span>
                </div>
                <h3 style="margin: 0 0 6px 0; color: #0F172A; font-weight: 800;">{t['symbol']}</h3>
                <p style="margin: 0 0 12px 0; color: #64748B; font-size: 13px;">💡 <b>Trigger:</b> {t['reason']}</p>
            </div>
            """)

            # Metric Columns
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("SL Level", f"₹{t['sl']:.1f}", f"-₹{risk:.1f}", delta_color="inverse")
            mc2.metric("Buy Price", f"₹{t['entry']:.1f}")
            mc3.metric("Target Level", f"₹{t['target']:.1f}", f"+₹{reward:.1f}")
            mc4.metric("Per Lot Risk", f"₹{risk * t['lot_size']:,.0f}", f"Target: ₹{reward * t['lot_size']:,.0f}")

            # Visual Risk vs Profit Bar Chart
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=['Trade Range'], x=[risk], name='Max Risk (Points)',
                orientation='h', marker=dict(color='#EF4444')
            ))
            fig_bar.add_trace(go.Bar(
                y=['Trade Range'], x=[reward], name='Max Profit (Points)',
                orientation='h', marker=dict(color='#10B981')
            ))
            fig_bar.update_layout(
                barmode='stack', height=80, margin=dict(l=0, r=0, t=0, b=0),
                showlegend=True, legend=dict(orientation="h", y=1.2)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{t['symbol']}")
            st.divider()

# ------------------------------------------------------------------
# TAB 2: MARKET BREADTH & VISUAL GAUGE METERS
# ------------------------------------------------------------------
with tab_breadth:
    col_gauge, col_ad = st.columns(2)

    with col_gauge:
        st.subheader("🎯 Put-Call Ratio (PCR) Gauge")
        pcr_val = 1.28
        
        fig_pcr = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pcr_val,
            title={'text': "PCR Sentiment Index"},
            gauge={
                'axis': {'range': [0, 2], 'tickwidth': 1},
                'bar': {'color': "#10B981"},
                'steps': [
                    {'range': [0, 0.7], 'color': '#FEE2E2'},    # Bearish
                    {'range': [0.7, 1.1], 'color': '#FEF3C7'},  # Neutral
                    {'range': [1.1, 2.0], 'color': '#D1FAE5'}   # Bullish
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': pcr_val
                }
            }
        ))
        fig_pcr.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pcr, use_container_width=True)

    with col_ad:
        st.subheader("📊 Market Advance / Decline Split")
        advances, declines = 38, 12
        
        fig_pie = px.pie(
            values=[advances, declines],
            names=['Advances (38)', 'Declines (12)'],
            color_discrete_sequence=['#10B981', '#EF4444'],
            hole=0.5
        )
        fig_pie.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Live Candlestick Chart
    st.subheader("📈 Live NIFTY 5-Min Chart")
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="5min")
    close_prices = np.cumsum(np.random.randn(30) * 1.5) + 24310
    open_prices = close_prices + np.random.randn(30) * 2
    high_prices = np.maximum(open_prices, close_prices) + np.random.rand(30) * 5
    low_prices = np.minimum(open_prices, close_prices) - np.random.rand(30) * 5

    fig_candle = go.Figure(data=[go.Candlestick(
        x=dates, open=open_prices, high=high_prices, low=low_prices, close=close_prices,
        increasing_line_color='#10B981', decreasing_line_color='#EF4444'
    )])
    fig_candle.update_layout(template="plotly_white", height=350, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_candle, use_container_width=True)

# ------------------------------------------------------------------
# TAB 3: MULTI-TRADE PORTFOLIO BUILDER
# ------------------------------------------------------------------
with tab_portfolio:
    st.subheader("✍️ Add Multiple Custom Positions")
    
    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    with st.form("add_trade_form_v2"):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            t_symbol = st.text_input("Option Strike", "NIFTY 24400 CE")
        with c2:
            t_entry = st.number_input("Entry Price (₹)", value=100.0, step=5.0)
        with c3:
            t_sl = st.number_input("SL Points (₹)", value=20.0, step=2.0)
        with c4:
            t_target = st.number_input("Target Points (₹)", value=40.0, step=5.0)
        with c5:
            c_lots = st.number_input("Lots", value=2, step=1)

        submitted = st.form_submit_button("➕ Add Position", use_container_width=True)

        if submitted:
            st.session_state.custom_trades.append({
                "Symbol": t_symbol,
                "Lots": c_lots,
                "Entry": t_entry,
                "Max Risk (₹)": c_lots * 65 * t_sl,
                "Max Profit (₹)": c_lots * 65 * t_target
            })
            st.success(f"Added {t_symbol} to Portfolio!")

    if st.session_state.custom_trades:
        df = pd.DataFrame(st.session_state.custom_trades)
        st.dataframe(df, use_container_width=True)

        tot_risk = df["Max Risk (₹)"].sum()
        tot_profit = df["Max Profit (₹)"].sum()

        m1, m2 = st.columns(2)
        m1.metric("Total Portfolio Risk", f"₹{tot_risk:,.2f}", delta_color="inverse")
        m2.metric("Total Potential Profit", f"₹{tot_profit:,.2f}")

        if st.button("🗑️ Clear Basket"):
            st.session_state.custom_trades = []
            st.rerun()
