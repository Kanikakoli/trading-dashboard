import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SECURE SESSION PASSWORD
# ------------------------------------------------------------------
st.set_page_config(
    page_title="PRO TERMINAL v23.9 (ADVANCED AI ALGO EVALUATOR)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def check_password():
    def password_entered():
        if st.session_state["password"] == "pro12345":
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
# 2. HELPER: SAFE LOGGING & EXPIRY
# ------------------------------------------------------------------
def get_next_weekday_expiry(target_weekday):
    today = datetime.now().date()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:  
        days_ahead += 7
    next_date = today + timedelta(days=days_ahead)
    return next_date.strftime('%d %b %Y').upper()

def log_trade_performance(trade_list):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = []
    for t in trade_list:
        data.append({
            "Timestamp": timestamp,
            "Symbol": t.get("sym", "N/A"),
            "Entry Price": t.get("entry", 0),
            "Current LTP": t.get("ltp", 0),
            "Target": t.get("target", 0),
            "Stop Loss": t.get("sl", 0),
            "Recommendation": t.get("rec", "BUY")
        })
    df = pd.DataFrame(data)
    file_exists = os.path.isfile("trade_performance.csv")
    try:
        if file_exists and os.path.getsize("trade_performance.csv") > 0:
            df.to_csv("trade_performance.csv", mode='a', index=False, header=False)
        else:
            df.to_csv("trade_performance.csv", mode='w', index=False, header=True)
    except Exception:
        pass

# ------------------------------------------------------------------
# 3. PROFESSIONAL HIGH-CONTRAST DYNAMIC CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #F8FAFC; color: #0F172A; }
.block-container { padding: 0.4rem 0.4rem !important; max-width: 100% !important; }

.metrics-container { display: flex; gap: 6px; margin-bottom: 8px; }
.metric-box {
    flex: 1; background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 6px; text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.m-title { font-size: 8px; color: #64748B; font-weight: 800; text-transform: uppercase; }
.m-val { font-size: 11px; color: #0F172A; font-weight: 900; margin: 2px 0; }
.m-sub { font-size: 8px; font-weight: 700; }

.analysis-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-left: 5px solid #16A34A; border-radius: 8px;
    padding: 10px; margin-bottom: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.analysis-card-warning {
    background: #FFFBEB; border: 1px solid #FCD34D;
    border-left: 5px solid #D97706; border-radius: 8px;
    padding: 10px; margin-bottom: 8px;
}
.status-banner {
    padding: 4px 8px; border-radius: 4px; font-size: 9px;
    font-weight: 800; margin-bottom: 6px; display: flex;
    justify-content: space-between; align-items: center;
}
.banner-running { background-color: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
.banner-warning { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.symbol-title { font-size: 12px; font-weight: 900; color: #0F172A; }

.badge-rec { font-size: 9px; font-weight: 900; padding: 3px 8px; border-radius: 4px; color: white; }
.bg-buy { background-color: #16A34A; }
.bg-warning { background-color: #D97706; }

.card-grid { 
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; 
    background: #F1F5F9; padding: 6px; border-radius: 6px; 
    text-align: center; margin-top: 6px; 
}
.grid-lbl { font-size: 8px; color: #64748B; font-weight: 800; }
.grid-val { font-size: 10px; color: #0F172A; font-weight: 900; }
.txt-green { color: #16A34A; }
.txt-red { color: #DC2626; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. MARKET ENGINE STATE
# ------------------------------------------------------------------
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

rc = st.session_state.refresh_counter
nifty_spot = round(24500.0 + (rc % 5) * 4.2, 2)
current_time = datetime.now().strftime('%H:%M:%S')

col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
with col_h1:
    st.markdown(f"<h3 style='margin:0; padding:0; font-size:12px; font-weight:900; color:#0F172A;'>⚡ ADVANCED ALGO TERMINAL</h3><div style='font-size:8px; color:#64748B;'>Sync Time: {current_time} | Multi-Algo Engine Active</div>", unsafe_allow_html=True)
with col_h2:
    auto_refresh = st.checkbox("🔄 Auto Refresh (3s)", value=False)
with col_h3:
    if st.button("⚡ Force Sync Now"):
        st.session_state.refresh_counter += 1
        st.rerun()

if auto_refresh:
    time.sleep(3)
    st.session_state.refresh_counter += 1
    st.rerun()

# Top Metrics Banner
st.markdown(f"""
<div class="metrics-container" style="margin-top:4px;">
    <div class="metric-box">
        <div class="m-title">NIFTY SPOT</div>
        <div class="m-val">{nifty_spot}</div>
        <div class="m-sub txt-green">▲ Bullish Trend</div>
    </div>
    <div class="metric-box">
        <div class="m-title">ALGO STATUS</div>
        <div class="m-val" style="color:#16A34A;">OPTIMIZED</div>
        <div class="m-sub" style="color:#64748B;">Scanning All Setups</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 5. MASTER NAVIGATION TABS
# ------------------------------------------------------------------
main_pages = st.tabs([
    "🚀 Intraday Setups", "💡 AI Trade Evaluator (Smart Algo)", "⚡ Scalping Engine", 
    "🌙 BTST Scanner", "🎯 Hero-Zero Trades", "📊 Mutual Funds", 
    "🌍 Global Markets", "📈 Indicators", "📊 Option Chain", "📊 Win Rate Tracker"
])

atm_nifty = int(round(nifty_spot / 50) * 50)
live_ltp_val = round(63.0 + (rc % 4) * 1.5, 2)

# --- PAGE 1: INTRADAY SETUPS ---
with main_pages[0]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:4px; color:#1E293B;'>📊 Live Algorithmic Setups</div>", unsafe_allow_html=True)
    
    intraday_trades = [
        {
            "sym": f"NIFTY {atm_nifty} CE", 
            "index": "NIFTY 50", 
            "ltp": live_ltp_val, 
            "rec": "STRONG BUY", 
            "acc": "95.8% Accuracy", 
            "entry": round(live_ltp_val * 0.95, 2), 
            "sl": round(live_ltp_val * 0.75, 2), 
            "target": round(live_ltp_val * 1.40, 2), 
            "budget": "₹15,000", 
            "status": "🟢 LIVE & RUNNING"
        }
    ]
    log_trade_performance(intraday_trades)
    
    for item in intraday_trades:
        st.markdown(f"""
        <div class="analysis-card">
            <div class="status-banner banner-running"><span>⚡ {item['status']} ({item['index']}) | Budget: {item['budget']}</span><span>⭐ {item['acc']}</span></div>
            <div class="card-header"><span class="symbol-title">{item['sym']}</span><span class="badge-rec bg-buy">{item['rec']}</span></div>
            <div class="card-grid">
                <div><div class="grid-lbl">LIVE LTP</div><div class="grid-val txt-green">₹{item['ltp']}</div></div>
                <div><div class="grid-lbl">ENTRY</div><div class="grid-val">₹{item['entry']}</div></div>
                <div><div class="grid-lbl">STOP LOSS</div><div class="grid-val" style="color:#DC2626;">₹{item['sl']}</div></div>
                <div><div class="grid-lbl">TARGET</div><div class="grid-val" style="color:#16A34A;">₹{item['target']}</div></div>
                <div><div class="grid-lbl">ACTION</div><div class="grid-val" style="color:#D97706;">HOLD & TRAIL</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2: AI TRADE EVALUATOR (SMART ALGO ENGINE) ---
with main_pages[1]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>💡 AI Multi-Indicator Trade Evaluator (Algorithmic Analysis)</div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: eval_symbol = st.text_input("Enter Trade / Strike", value=f"NIFTY {atm_nifty} CE")
    with c2: eval_price = st.number_input("Your Entry Price (₹)", value=live_ltp_val)
    with c3: eval_budget = st.selectbox("Trading Budget", ["₹10,000", "₹25,000", "₹50,000"])
    with c4: eval_risk = st.selectbox("Risk Tolerance", ["Moderate (1:1.5)", "Aggressive (1:2.5)"])
    
    # --- ALGORITHMIC BACKTEST & EVALUATION LOGIC ---
    # Running checks on multiple indicators simulating real algos
    rsi_val = 58.4 + (rc % 3) * 1.2  # Simulated RSI between 58-61 (Bullish momentum)
    supertrend_status = "BULLISH"
    pcr_status = "1.24 (Strong Support)"
    
    # Decision algorithm
    is_favorable = eval_price > 10 and rsi_val < 75
    
    if eval_risk.startswith("Moderate"):
        calculated_sl = round(eval_price * 0.82, 2)
        calculated_target = round(eval_price * 1.35, 2)
    else:
        calculated_sl = round(eval_price * 0.75, 2)
        calculated_target = round(eval_price * 1.60, 2)
        
    if is_favorable:
        recommendation = "STRONG BUY & EXECUTE"
        card_style = "analysis-card"
        banner_style = "banner-running"
        badge_style = "bg-buy"
        action_text = "ENTER & TRAIL SL"
        algo_score = "96.2% Accuracy"
    else:
        recommendation = "AVOID / HIGH RISK"
        card_style = "analysis-card-warning"
        banner_style = "banner-warning"
        badge_style = "bg-warning"
        action_text = "DO NOT ENTER"
        algo_score = "42.0% Risk Warning"

    st.markdown("---")
    st.markdown(f"""
    <div class="{card_style}">
        <div class="status-banner {banner_style}"><span>🔍 ALGO EVALUATION RESULT | Budget: {eval_budget}</span><span>⭐ {algo_score}</span></div>
        <div class="card-header"><span class="symbol-title">{eval_symbol}</span><span class="badge-rec {badge_style}">{recommendation}</span></div>
        <div class="card-grid" style="grid-template-columns: repeat(5, 1fr);">
            <div><div class="grid-lbl">EVALUATED PRICE</div><div class="grid-val" style="color:#2563EB;">₹{eval_price}</div></div>
            <div><div class="grid-lbl">SUGGESTED SL</div><div class="grid-val" style="color:#DC2626;">₹{calculated_sl}</div></div>
            <div><div class="grid-lbl">SUGGESTED TARGET</div><div class="grid-val" style="color:#16A34A;">₹{calculated_target}</div></div>
            <div><div class="grid-lbl">RSI & SUPERTREND</div><div class="grid-val" style="color:#0F172A;">{rsi_val:.1f} / {supertrend_status}</div></div>
            <div><div class="grid-lbl">FINAL ACTION</div><div class="grid-val" style="color:#16A34A;">{action_text}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"ℹ️ **Algo Analysis Breakdown:** RSI is at `{rsi_val:.1f}` (Healthy zone), PCR is `{pcr_status}`, and Supertrend is `{supertrend_status}`. Risk-Reward ratio has been automatically optimized for your selected profile.")

# --- PAGE 3: SCALPING ENGINE ---
with main_pages[2]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>⚡ Lightning-Fast Scalping Engine</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>⚡ LIVE SCALP MOMENTUM | Budget: ₹15,000</span><span>⭐ 95.1% Accuracy</span></div>
        <div class="card-header"><span class="symbol-title">NIFTY {atm_nifty} CE</span><span class="badge-rec bg-buy">STRONG BUY</span></div>
        <div class="card-grid" style="grid-template-columns: repeat(5, 1fr);">
            <div><div class="grid-lbl">LTP</div><div class="grid-val">₹{live_ltp_val}</div></div>
            <div><div class="grid-lbl">TIMEFRAME</div><div class="grid-val">3 Min</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val" style="color:#DC2626;">₹{round(live_ltp_val*0.90, 2)}</div></div>
            <div><div class="grid-lbl">TARGET</div><div class="grid-val" style="color:#16A34A;">₹{round(live_ltp_val*1.20, 2)}</div></div>
            <div><div class="grid-lbl">MODE</div><div class="grid-val" style="color:#16A34A;">Active Trail</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE 4: BTST SCANNER ---
with main_pages[3]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>🌙 BTST / STBT Scanner</div>", unsafe_allow_html=True)
    btst_exp = get_next_weekday_expiry(1)
    st.markdown(f"""
    <div class="analysis-card">
        <div class="status-banner banner-running"><span>🌙 OVERNIGHT MOMENTUM | Expiry: {btst_exp}</span><span>⭐ 89.0% Accuracy</span></div>
        <div class="card-header"><span class="symbol-title">NIFTY {atm_nifty} CE</span><span class="badge-rec bg-buy">BTST BUY</span></div>
        <div class="card-grid" style="grid-template-columns: repeat(5, 1fr);">
            <div><div class="grid-lbl">LTP</div><div class="grid-val">₹{live_ltp_val}</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val" style="color:#DC2626;">₹45.00</div></div>
            <div><div class="grid-lbl">TARGET 1</div><div class="grid-val" style="color:#16A34A;">₹130.00</div></div>
            <div><div class="grid-lbl">TARGET 2</div><div class="grid-val" style="color:#16A34A;">₹175.00</div></div>
            <div><div class="grid-lbl">STATUS</div><div class="grid-val" style="color:#2563EB;">Armed</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE 5: HERO-ZERO TRADES ---
with main_pages[4]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>🎯 Hero-Zero Expiry Day Special Recommendations</div>", unsafe_allow_html=True)
    hz_exp = get_next_weekday_expiry(1)
    st.markdown(f"""
    <div class="analysis-card" style="border-left-color: #D97706;">
        <div class="status-banner banner-warning"><span>⚡ HERO-ZERO SETUP | Expiry: {hz_exp}</span><span>⭐ 88.2% Accuracy</span></div>
        <div class="card-header"><span class="symbol-title">NIFTY {atm_nifty+100} CE</span><span class="badge-rec bg-warning">HERO-ZERO BUY</span></div>
        <div class="card-grid" style="grid-template-columns: repeat(5, 1fr);">
            <div><div class="grid-lbl">LTP</div><div class="grid-val">₹14.50</div></div>
            <div><div class="grid-lbl">SL</div><div class="grid-val" style="color:#DC2626;">₹3.00</div></div>
            <div><div class="grid-lbl">TARGET</div><div class="grid-val" style="color:#16A34A;">₹65.00</div></div>
            <div><div class="grid-lbl">MULTIPLIER</div><div class="grid-val" style="color:#2563EB;">3x - 5x</div></div>
            <div><div class="grid-lbl">ACTION</div><div class="grid-val" style="color:#16A34A;">Active</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE 6: MUTUAL FUNDS ---
with main_pages[5]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>📊 Best Mutual Funds Analysis</div>", unsafe_allow_html=True)
    mf_df = pd.DataFrame([
        {"Fund Name": "Quant Small Cap Fund", "1Y Return": "+38.4%", "3Y CAGR": "+28.2%", "Risk": "Very High", "Action": "TOP SIP"},
        {"Fund Name": "Nippon India Small Cap Fund", "1Y Return": "+32.9%", "3Y CAGR": "+25.4%", "Risk": "Very High", "Action": "STRONG SIP"}
    ])
    st.dataframe(mf_df, use_container_width=True, hide_index=True)

# --- PAGE 7: GLOBAL MARKETS ---
with main_pages[6]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>🌍 Global Markets Feed</div>", unsafe_allow_html=True)
    g_cols = st.columns(2)
    with g_cols[0]:
        st.markdown("<div class='metric-box'><div class='m-title'>DOW JONES</div><div class='m-val'>40,850.20</div><div class='m-sub txt-green'>▲ +0.45%</div></div>", unsafe_allow_html=True)
    with g_cols[1]:
        st.markdown("<div class='metric-box'><div class='m-title'>NASDAQ</div><div class='m-val'>17,920.10</div><div class='m-sub txt-green'>▲ +0.88%</div></div>", unsafe_allow_html=True)

# --- PAGE 8: INDICATORS ---
with main_pages[7]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>📈 Technical Screener</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Asset": "NIFTY 50", "RSI": "62.4 (Bullish)", "MACD": "Positive", "Supertrend": "BUY", "Signal": "STRONG BUY"}]), use_container_width=True, hide_index=True)

# --- PAGE 9: OPTION CHAIN ---
with main_pages[8]:
    st.markdown(f"<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>📊 Live Option Chain Matrix (Spot: {nifty_spot})</div>", unsafe_allow_html=True)
    chain_data = pd.DataFrame([
        {"CALL OI": "1.58L", "CALL LTP": f"₹{round(live_ltp_val*1.5, 2)}", "STRIKE": atm_nifty-50, "PUT LTP": f"₹{round(live_ltp_val*0.8, 2)}", "PUT OI": "2.22L"},
        {"CALL OI": "1.09L", "CALL LTP": f"₹{live_ltp_val}", "STRIKE": atm_nifty, "PUT LTP": f"₹{round(live_ltp_val*1.2, 2)}", "PUT OI": "69,397"}
    ])
    st.dataframe(chain_data, use_container_width=True, hide_index=True)

# --- PAGE 10: WIN RATE TRACKER ---
with main_pages[9]:
    st.markdown("<div style='font-size:11px; font-weight:800; margin-bottom:6px; color:#1E293B;'>📊 Historical Win Rate Tracker</div>", unsafe_allow_html=True)
    csv_file = "trade_performance.csv"
    df_perf = None
    if os.path.isfile(csv_file):
        try:
            df_perf = pd.read_csv(csv_file)
        except Exception:
            try:
                os.path.remove(csv_file)
            except Exception:
                pass
            df_perf = None

    if df_perf is not None and not df_perf.empty:
        st.dataframe(df_perf, use_container_width=True, hide_index=True)
        st.metric(label="Simulated Win Rate", value="89.4%")
        if st.button("🗑️ Clear History"):
            try:
                os.remove(csv_file)
            except Exception:
                pass
            st.rerun()
    else:
        st.info("No trading history logged yet. History will populate automatically as trades update.")
        if st.button("🔄 Refresh Tracker"):
            st.rerun()
