import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v8.3 | Compact Mobile Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------
# SECURITY LOCK
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

def render_html(html_str):
    st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)

# ------------------------------------------------------------------
# COMPACT CSS (ELIMINATES MOBILE SPACE WASTAGE)
# ------------------------------------------------------------------
render_html("""
<style>
    /* Global Spacing Reduction */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Horizontal Ticker Grid for Mobile */
    .ticker-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .ticker-chip {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 6px 10px;
        flex: 1 1 calc(33.33% - 6px);
        min-width: 95px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .chip-title { font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase; }
    .chip-val { font-size: 12px; font-weight: 800; color: #0F172A; }
    .chip-up { font-size: 10px; color: #10B981; font-weight: 700; }
    .chip-down { font-size: 10px; color: #EF4444; font-weight: 700; }

    /* Compact Trade Card */
    .compact-trade-card {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .card-call-border { border-left: 5px solid #10B981; }
    .card-put-border { border-left: 5px solid #EF4444; }

    .card-header-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .strike-title { font-size: 16px; font-weight: 800; color: #0F172A; margin: 0; }
    
    .badge-pill-call { background: #D1FAE5; color: #065F46; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; }
    .badge-pill-put { background: #FEE2E2; color: #991B1B; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; }

    /* Compact Grid for Metrics inside Card */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 4px;
        background: #F8FAFC;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        margin-top: 8px;
    }
    .m-label { font-size: 9px; color: #64748B; font-weight: 700; }
    .m-val { font-size: 13px; font-weight: 800; color: #0F172A; }
    .m-sub-up { font-size: 9px; color: #10B981; font-weight: 700; }
    .m-sub-down { font-size: 9px; color: #EF4444; font-weight: 700; }

    /* CSS Visual Risk/Reward Bar */
    .rr-bar-container {
        height: 8px;
        width: 100%;
        background: #E2E8F0;
        border-radius: 4px;
        display: flex;
        overflow: hidden;
        margin-top: 8px;
    }
    .rr-risk { background: #EF4444; height: 100%; }
    .rr-reward { background: #10B981; height: 100%; }
</style>
""")

# ------------------------------------------------------------------
# HEADER & SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚡ Settings")
    if st.button("🔒 Lock Terminal", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.title("⚡ OPTION TERMINAL v8.3")

# ------------------------------------------------------------------
# 1. COMPACT HORIZONTAL GLOBAL TICKERS
# ------------------------------------------------------------------
render_html("""
<div class="ticker-bar">
    <div class="ticker-chip">
        <div class="chip-title">GIFT NIFTY</div>
        <div class="chip-val">24,380.0</div>
        <div class="chip-up">▲ +120.0</div>
    </div>
    <div class="ticker-chip">
        <div class="chip-title">S&P 500</div>
        <div class="chip-val">5,560.2</div>
        <div class="chip-up">▲ +34.5</div>
    </div>
    <div class="ticker-chip">
        <div class="chip-title">NASDAQ</div>
        <div class="chip-val">18,240.1</div>
        <div class="chip-up">▲ +180.2</div>
    </div>
    <div class="ticker-chip">
        <div class="chip-title">NIKKEI 225</div>
        <div class="chip-val">38,910.5</div>
        <div class="chip-down">▼ -45.0</div>
    </div>
    <div class="ticker-chip">
        <div class="chip-title">INDIA VIX</div>
        <div class="chip-val">13.20</div>
        <div class="chip-down">▼ -2.4%</div>
    </div>
</div>
""")

# ------------------------------------------------------------------
# 2. TABS ARCHITECTURE
# ------------------------------------------------------------------
tab_signals, tab_breadth, tab_portfolio = st.tabs([
    "⚡ Active Signals", 
    "📊 Market Sentiment", 
    "✍️ Multi-Trade Basket"
])

# ------------------------------------------------------------------
# TAB 1: ULTRA-COMPACT TRADE SIGNALS
# ------------------------------------------------------------------
with tab_signals:
    filter_index = st.selectbox("Filter:", ["ALL", "NIFTY 50", "BANK NIFTY", "SENSEX"], label_visibility="collapsed")

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
        rr = reward / risk if risk > 0 else 1
        is_call = "CALL" in t['type']

        card_border = "card-call-border" if is_call else "card-put-border"
        badge_pill = "badge-pill-call" if is_call else "badge-pill-put"

        # Calculate percentages for the CSS progress bar
        total_range = risk + reward
        risk_pct = (risk / total_range) * 100
        reward_pct = (reward / total_range) * 100

        render_html(f"""
        <div class="compact-trade-card {card_border}">
            <div class="card-header-flex">
                <div>
                    <span class="{badge_pill}">{t['type']}</span>
                    <span style="font-size: 11px; font-weight: 700; color: #64748B; margin-left: 6px;">RR 1:{rr:.1f}</span>
                </div>
                <div style="font-size: 10px; font-weight: 700; color: #475569;">Lot Size: {t['lot_size']}</div>
            </div>
            
            <div class="strike-title">{t['symbol']}</div>
            <div style="font-size: 11px; color: #475569; margin-top: 2px;">💡 {t['reason']}</div>
            
            <div class="metrics-grid">
                <div>
                    <div class="m-label">BUY ENTRY</div>
                    <div class="m-val">₹{t['entry']:.0f}</div>
                </div>
                <div>
                    <div class="m-label">STOP LOSS</div>
                    <div class="m-val">₹{t['sl']:.0f}</div>
                    <div class="m-sub-down">-₹{risk:.0f}</div>
                </div>
                <div>
                    <div class="m-label">TARGET</div>
                    <div class="m-val">₹{t['target']:.0f}</div>
                    <div class="m-sub-up">+₹{reward:.0f}</div>
                </div>
                <div>
                    <div class="m-label">LOT RISK</div>
                    <div class="m-val">₹{risk * t['lot_size']:,.0f}</div>
                    <div class="m-sub-up">T: ₹{reward * t['lot_size']:,.0f}</div>
                </div>
            </div>

            <div class="rr-bar-container" title="Risk: {risk_pct:.0f}% | Reward: {reward_pct:.0f}%">
                <div class="rr-risk" style="width: {risk_pct}%;"></div>
                <div class="rr-reward" style="width: {reward_pct}%;"></div>
            </div>
        </div>
        """)

# ------------------------------------------------------------------
# TAB 2: MARKET BREADTH & CHART
# ------------------------------------------------------------------
with tab_breadth:
    col1, col2 = st.columns(2)
    with col1:
        st.caption("🎯 Put-Call Ratio (PCR)")
        fig_pcr = go.Figure(go.Indicator(
            mode="gauge+number",
            value=1.28,
            gauge={
                'axis': {'range': [0, 2]},
                'bar': {'color': "#10B981"},
                'steps': [
                    {'range': [0, 0.7], 'color': '#FEE2E2'},
                    {'range': [0.7, 1.1], 'color': '#FEF3C7'},
                    {'range': [1.1, 2.0], 'color': '#D1FAE5'}
                ]
            }
        ))
        fig_pcr.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pcr, use_container_width=True)

    with col2:
        st.caption("📊 Advance / Decline Split")
        fig_pie = px.pie(
            values=[38, 12], names=['Adv (38)', 'Dec (12)'],
            color_discrete_sequence=['#10B981', '#EF4444'], hole=0.5
        )
        fig_pie.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------------
# TAB 3: PORTFOLIO BASKET BUILDER
# ------------------------------------------------------------------
with tab_portfolio:
    if 'custom_trades' not in st.session_state:
        st.session_state.custom_trades = []

    with st.form("compact_form"):
        st.caption("➕ Quick Add Position")
        f1, f2, f3, f4 = st.columns(4)
        with f1: t_symbol = st.text_input("Strike", "NIFTY 24400 CE")
        with f2: t_entry = st.number_input("Entry (₹)", value=100.0)
        with f3: t_sl = st.number_input("SL Points", value=20.0)
        with f4: t_target = st.number_input("Target Points", value=40.0)
        
        submitted = st.form_submit_button("Add Position", use_container_width=True)

        if submitted:
            st.session_state.custom_trades.append({
                "Symbol": t_symbol,
                "Entry": t_entry,
                "Risk (₹)": 65 * t_sl,
                "Reward (₹)": 65 * t_target
            })
            st.success("Added!")

    if st.session_state.custom_trades:
        df = pd.DataFrame(st.session_state.custom_trades)
        st.dataframe(df, use_container_width=True)
        if st.button("Clear Basket", use_container_width=True):
            st.session_state.custom_trades = []
            st.rerun()

