import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
import yfinance as yf
from data_engine import get_stock_data, analyze_signals, generate_trading_plan, screen_all_stocks, allocate_funds, get_daily_alerts_and_news, check_emergency_alerts, generate_rotation_plan


import json
import os

PORTFOLIO_FILE = "user_portfolios.json"

def load_portfolios():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_portfolios(data):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.set_page_config(page_title="Jarvis Terminal", layout="wide", page_icon="⚡", initial_sidebar_state="expanded")

# ... (CSS stays the same, I'll search for the header to insert the banner)


custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

/* GLOBAL RESETS & FONTS */
html, body, [class*="st-"] {
    font-family: 'Prompt', sans-serif;
}
.stIcon, .material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
}

/* APP BACKGROUND (MESH GRADIENT) */
.stApp {
    background: radial-gradient(circle at 15% 50%, rgba(0, 255, 163, 0.05), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.05), transparent 25%);
    background-color: #0F172A;
}

/* LAYOUT & RESPONSIVE PADDING */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
    animation: fadeIn 0.8s ease-out;
}
#MainMenu, footer, header {visibility: hidden;}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* --- INFOGRAPHIC METRIC CARDS --- */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(30,41,59,0.7) 0%, rgba(15,23,42,0.9) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    border-top: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #00FFA3, #00B8FF);
    opacity: 0;
    transition: opacity 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px -10px rgba(0,255,163,0.15);
    border-color: rgba(0,255,163,0.3);
}
[data-testid="stMetric"]:hover::before { opacity: 1; }

[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-size: 36px !important;
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #FFF, #00FFA3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 4px 20px rgba(0,255,163,0.2);
}

/* --- GLASS TABS --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(30,41,59,0.5);
    backdrop-filter: blur(10px);
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    border: none !important;
    color: #64748B !important;
    font-weight: 600;
    font-size: 16px;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background: rgba(255,255,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00FFA3 0%, #00B8FF 100%) !important;
    color: #0F172A !important;
    box-shadow: 0 4px 15px rgba(0,255,163,0.3) !important;
}

/* --- MODERN BUTTONS --- */
.stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.3) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.5) !important;
    background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%) !important;
}

/* --- RESPONSIVE TYPOGRAPHY & MEDIA QUERIES --- */
h1, h2, h3 {
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}
h3 {
    background: -webkit-linear-gradient(45deg, #F8FAFC, #94A3B8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem !important;
}

/* Mobile Adjustments (Phones) */
@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 14px;
        width: 100%;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-direction: column;
    }
}

/* Tablet Adjustments (iPads) */
@media (min-width: 769px) and (max-width: 1024px) {
    [data-testid="stMetricValue"] { font-size: 32px !important; }
    .stTabs [data-baseweb="tab"] { padding: 10px 15px !important; }
}

/* --- DATAFRAME UPGRADES --- */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 30px -15px rgba(0,0,0,0.5);
}

/* Custom Infographic Title */
.gradient-text {
    background: linear-gradient(90deg, #00FFA3, #00B8FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3em;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0px;
    padding-bottom: 0px;
}
.sub-text {
    text-align: center;
    color: #94A3B8;
    font-size: 1.2em;
    font-weight: 400;
    margin-top: 5px;
    margin-bottom: 30px;
    letter-spacing: 2px;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='gradient-text'>JARVIS TRADING</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>AI QUANTITATIVE ANALYSIS & PORTFOLIO ROTATION</p>", unsafe_allow_html=True)

watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "RGTI", "RKLB", "SHOP", "JEPQ", "AMD", "TSM"]

@st.cache_data(ttl=3600)
def load_data(ticker, period):
    return get_stock_data(ticker, period)

# --- SIDEBAR (Settings & Navigation) ---
with st.sidebar:
    st.markdown("### ⚙️ การตั้งค่า (Settings)")
    st.markdown("---")
    
    selected_ticker = st.selectbox("🎯 เลือกหุ้นที่ต้องการวิเคราะห์:", watchlist, index=0)
    
    st.caption("หรือพิมพ์ชื่อหุ้นตัวอื่น:")
    custom_ticker = st.text_input("Custom Ticker (e.g. NFLX)", value="").upper()
    if custom_ticker and custom_ticker != "":
        selected_ticker = custom_ticker
        
    period = st.selectbox("📅 กรอบเวลาย้อนหลัง (Timeframe):", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
    
    st.markdown("---")
    if st.button("🔄 อัปเดตข้อมูลตลาด (Refresh)"):
        st.cache_data.clear()
        st.rerun()

# --- MAIN DASHBOARD HEADER ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>⚡ JARVIS COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a3a8b8; margin-bottom: 30px; font-size: 1.1rem;'>ระบบผู้ช่วยสแกนหุ้นและจัดสรรพอร์ตอัตโนมัติ (Automated Swing Trade Assistant)</p>", unsafe_allow_html=True)

# --- EMERGENCY PANIC ROOM BANNER ---
@st.cache_data(ttl=1800) # Cache for 30 mins so it doesn't slow down the app every click
def run_emergency_scan(tickers):
    return check_emergency_alerts(tickers)

emergencies = run_emergency_scan(watchlist)

if emergencies:
    st.markdown("""
    <style>
    @keyframes emergency-flash {
        0% { background-color: rgba(239, 68, 68, 0.2); border: 2px solid rgba(239, 68, 68, 0.5); box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
        50% { background-color: rgba(239, 68, 68, 0.6); border: 2px solid rgba(255, 255, 255, 0.8); box-shadow: 0 0 30px rgba(239, 68, 68, 0.8); }
        100% { background-color: rgba(239, 68, 68, 0.2); border: 2px solid rgba(239, 68, 68, 0.5); box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
    }
    .panic-room {
        animation: emergency-flash 1.5s infinite;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        text-align: center;
        color: white;
    }
    .panic-item {
        font-size: 18px;
        margin: 10px 0;
        background: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    html_content = "<div class='panic-room'><h3>🚨 สัญญาณเตือนภัยด่วน (EMERGENCY ALERTS) 🚨</h3>"
    for em in emergencies:
        html_content += f"<div class='panic-item'><b>[{em['Ticker']}] {em['Type']}</b><br/><span style='font-size: 15px;'>{em['Message']}</span></div>"
    html_content += "</div>"
    
    st.markdown(html_content, unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs(["📈 วางแผนเทรด (Trade)", "💼 สแกนพอร์ต (Portfolio)", "🚨 เรดาร์ตลาด (Radar)", "🔄 สับเปลี่ยนหุ้น (Rotation)"])

# --- TAB 1: Single Stock Analysis ---
with tab1:
    df, info = load_data(selected_ticker, period)
    
    if df is None:
        st.error(f"❌ ไม่พบข้อมูลสำหรับหุ้น {selected_ticker} หรือตลาดยังไม่เปิด")
    else:
        latest_close = df['Close'].iloc[-1]
        signals = analyze_signals(df)
        
        # 4-Column Metric Header (Modern Top Bar)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 ราคาปัจจุบัน (Price)", f"${latest_close:.2f}")
        with col2:
            res_val = df['Resistance'].iloc[-1]
            st.metric("🎯 เป้าขาย (Resistance)", f"${res_val:.2f}" if pd.notna(res_val) else "N/A")
        with col3:
            sup_val = df['Support'].iloc[-1]
            st.metric("🛑 จุดตัดขาดทุน (Cut Loss)", f"${sup_val:.2f}" if pd.notna(sup_val) else "N/A")
        with col4:
            rsi_val = df['RSI'].iloc[-1]
            st.metric("🔥 โมเมนตัม (RSI)", f"{rsi_val:.1f}" if pd.notna(rsi_val) else "N/A")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action Plan Generation (Auto)
        plan = generate_trading_plan(df)
        
        # Interactive Chart spanning full width
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#f59e0b', width=2), name='SMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#3b82f6', width=2), name='SMA 200'))
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1), name='BB Upper', showlegend=False))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)', name='Bollinger Bands'))
        
        fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='#ef4444', width=1.5, dash='dash'), name='Resistance'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='#10b981', width=1.5, dash='dash'), name='Support'))
        
        # Add Forecasting Arrow based on Plan
        if "error" not in plan and "status" in plan:
            latest_date = df.index[-1]
            # Fast forward ~7 days for the arrow target (visual only)
            future_date = latest_date + timedelta(days=7)
            
            if plan["status"] in ["BUY_DIP", "BUY_BREAK"]:
                target_price = plan['sell_target']
                arrow_color = '#10b981' # Green
                text = "📈 แนวโน้มขึ้น (UPTREND)"
            elif plan["status"] == "WAIT_DIP":
                target_price = plan['buy_target'] # Predict drop to support
                arrow_color = '#ef4444' # Red
                text = "📉 แนวโน้มย่อตัว (PULLBACK)"
            else: # WAIT_BREAK
                target_price = plan['sell_target'] 
                arrow_color = '#f59e0b' # Yellow
                text = "⚠️ ทดสอบแนวต้าน (TESTING)"
                
            fig.add_annotation(
                x=future_date,
                y=target_price,
                ax=latest_date,
                ay=latest_close,
                xref="x", yref="y",
                axref="x", ayref="y",
                text=text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor=arrow_color,
                font=dict(color=arrow_color, size=14, family="Prompt")
            )
            # Add a dotted line representing the expected path
            fig.add_trace(go.Scatter(
                x=[latest_date, future_date], 
                y=[latest_close, target_price], 
                mode='lines',
                line=dict(color=arrow_color, width=2, dash='dot'),
                showlegend=False
            ))

        fig.update_layout(
            title=dict(text=f"{selected_ticker} - Technical Analysis & AI Forecast", font=dict(size=18, family="Prompt")),
            yaxis_title='Price (USD)',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=450,
            margin=dict(l=0, r=0, t=50, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if "error" in plan:
            st.warning(f"⚠️ ข้อมูลไม่เพียงพอ: {plan['error']}")
        else:
            st.markdown("### 🎯 แผนการเทรดที่ระบบแนะนำ (AI Action Plan)")
            
            if "status" in plan:
                if plan["status"] == "WAIT_DIP":
                    st.info("🟡 **คำแนะนำ:** ราคายังอยู่กลางทาง ควรรอให้ย่อตัวลงมาใกล้โซนซื้อ (Support) ค่อยเข้า")
                elif plan["status"] == "BUY_DIP":
                    st.success("🟢 **คำแนะนำ:** ราคาลงมาใกล้แนวรับแล้ว เป็นจังหวะ 'ทยอยเก็บของ' (Buy the Dip)")
                elif plan["status"] == "WAIT_BREAK":
                    st.info("🟡 **คำแนะนำ:** ราคาจ่อทะลุแนวต้าน ควรรอให้ทะลุแน่ๆ ค่อยเข้าซื้อตาม (Buy on Breakout)")
                elif plan["status"] == "BUY_BREAK":
                    st.success("🟢 **คำแนะนำ:** ราคาเบรกทะลุแนวต้านแล้ว เป็นจังหวะ 'ตามน้ำ' (Breakout Play)")
                    
            st.markdown("---")
            
            if "buy_target" in plan and "cut_loss" in plan and "sell_target" in plan:
                risk = plan['buy_target'] - plan['cut_loss']
                reward = plan['sell_target'] - plan['buy_target']
                if risk > 0 and reward > 0:
                    rr_ratio = reward / risk
                    if rr_ratio >= 2:
                        st.success(f"✅ ความคุ้มค่าสูง: กำไรมากกว่าความเสี่ยง 2 เท่าขึ้นไป (R/R = 1:{rr_ratio:.2f})")
                    else:
                        st.warning(f"⚠️ ความคุ้มค่าปานกลาง: (R/R = 1:{rr_ratio:.2f}) แนะนำให้ระมัดระวังในการเข้าไม้ใหญ่")
                        
            st.markdown("*(สำหรับคนที่ถือหุ้นอยู่แล้ว หรือต้องการกดซื้อทันที ณ ราคาปัจจุบัน)*")
            st.caption(f"หากกดซื้อที่ราคา ${plan['immediate']['current_price']:.2f} ตอนนี้ -> เป้าทำกำไรคือ **${plan['immediate']['buy_target']:.2f}** และจุดหนีตายคือ **${plan['immediate']['buy_cut_loss']:.2f}**")


# --- TAB 2: Money Management & Screener ---
with tab2:
    st.markdown("### 💼 ระบบสแกนและกระจายเงินลงทุนอัตโนมัติ")
    st.markdown("ระบบจะกวาดสายตาสแกนหุ้นใน Watchlist ทั้งหมด เพื่อคัดเฉพาะตัวที่กราฟแข็งแกร่ง และแบ่งเงินให้คุณโดยอัตโนมัติ")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        invest_amount = st.number_input("💵 เงินทุนเตรียมเข้าซื้อ (USD):", min_value=1.0, value=100.0, step=10.0)
        max_picks = st.slider("🔢 จัดสรรเงินให้หุ้นกี่ตัว (Max Picks):", min_value=1, max_value=len(watchlist), value=5)
        scan_btn = st.button("🚀 สแกนตลาด")
        
    if scan_btn:
        with st.spinner("กำลังสแกนหุ้นทุกตัว..."):
            screener_df = screen_all_stocks(watchlist, period)
            msg, alloc_df = allocate_funds(screener_df, invest_amount, max_picks)
            
            st.success(msg)
            
            if not alloc_df.empty:
                r1_col1, r1_col2 = st.columns([1.5, 1])
                with r1_col1:
                    st.markdown("#### 🛒 โผหุ้นที่ควรเข้าซื้อ (Buy List)")
                    st.dataframe(alloc_df[['Ticker', 'Status', 'Allocation ($)']].style.format({'Allocation ($)': '${:.2f}'}), use_container_width=True)
                with r1_col2:
                    fig_pie = px.pie(alloc_df, values='Allocation ($)', names='Ticker', hole=0.45)
                    fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            # --- SELL LIST SECTION ---
            sell_df = screener_df[screener_df['Score'] <= 0].copy()
            if not sell_df.empty:
                st.markdown("---")
                st.markdown("#### 🗑️ โผหุ้นที่ควรพิจารณาขาย / หลีกเลี่ยง (Sell & Avoid List)")
                st.warning("⚠️ หุ้นกลุ่มนี้กำลังอยู่ในโซนอันตราย (Overbought สุดๆ หรือกราฟพังเป็นขาลง) หากมีของอยู่ควรพิจารณาล็อกกำไร/ตัดขาดทุน หรือห้ามเข้าซื้อเด็ดขาด!")
                styled_sell = sell_df[['Ticker', 'Price', 'RSI', 'Status']].style.format({'Price': '${:.2f}', 'RSI': '{:.1f}'}).background_gradient(subset=['RSI'], cmap='Reds', vmin=30, vmax=80)
                st.dataframe(styled_sell, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📊 อัปเดตสถานะหุ้นทั้งหมด (Live Market Status)")
            styled_all = screener_df[['Ticker', 'Price', 'RSI', 'Score', 'Status']].style.format({'Price': '${:.2f}', 'RSI': '{:.1f}', 'Score': '{:.1f}'}).background_gradient(subset=['Score'], cmap='RdYlGn', vmin=-2, vmax=10)
            st.dataframe(styled_all, use_container_width=True)


# --- TAB 3: Daily News & Alerts ---
with tab3:
    st.markdown("### 🚨 เรดาร์จับความผันผวน & ข่าวกรอง (Market Radar)")
    st.markdown("สแกนหา 'ความผิดปกติ' ของราคาหุ้น และสรุปพาดหัวข่าวสำคัญที่ส่งผลกระทบต่อราคาโดยตรง")
    
    if st.button("📡 กวาดสัญญาณตลาด (Scan Radar)"):
        with st.spinner("กำลังประมวลผลข้อมูลความผันผวนและข่าวจาก Wall Street..."):
            alerts, news_feed = get_daily_alerts_and_news(watchlist)
            
            if alerts:
                st.markdown("#### ⚠️ หุ้นที่ต้องระวังการสวิงแรง (Volatility Alerts)")
                for alert in alerts:
                    if "สวิงลง" in alert['Alert'] or "ลบกดดัน" in alert['Alert']:
                        st.error(f"**[{alert['Ticker']}]** {alert['Alert']} - {alert['Details']}")
                    else:
                        st.success(f"**[{alert['Ticker']}]** {alert['Alert']} - {alert['Details']}")
            else:
                st.info("✅ วันนี้ตลาดยังสงบดี ไม่มีหุ้นตัวไหนสวิงแรงผิดปกติครับ")
                
            st.markdown("---")
            st.markdown("#### 🗞️ ข่าวที่กระทบต่อราคา (Actionable Catalyst)")
            
            if news_feed:
                for item in news_feed:
                    if item['Color'] == 'green':
                        st.success(f"🟢 **[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*")
                    elif item['Color'] == 'red':
                        st.error(f"🔴 **[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*")
                    else:
                        st.info(f"🔵 **[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*")
            else:
                st.write("ไม่มีข่าวเด่นที่ตรงกับความผันผวนในขณะนี้")

# --- TAB 4: Smart Portfolio Rotation ---
with tab4:
    st.markdown("### 🔄 ระบบสับเปลี่ยนหุ้นอัตโนมัติ (Smart Rotation)")
    st.markdown("เลือกระบุโปรไฟล์ของคุณ หรือสร้างใหม่เพื่อบันทึกพอร์ตส่วนตัวของคุณเอง (ไม่ต้องใช้รหัสผ่าน)")
    
    portfolios_db = load_portfolios()
    profile_names = list(portfolios_db.keys())
    
    st.markdown("#### 👤 1. เลือกหรือสร้างโปรไฟล์ผู้ใช้งาน")
    col_sel, col_new = st.columns([1, 1])
    
    with col_sel:
        options = ["-- เลือกโปรไฟล์ --"] + profile_names
        # Default index handling
        selected_profile = st.selectbox("รายชื่อโปรไฟล์ที่มีอยู่:", options)
        
    with col_new:
        new_profile_name = st.text_input("➕ สร้างโปรไฟล์ใหม่ (พิมพ์ชื่อแล้วกดสร้าง):")
        if st.button("บันทึกชื่อใหม่"):
            if new_profile_name and new_profile_name not in portfolios_db:
                portfolios_db[new_profile_name] = [{"Ticker": "AAPL", "Current Value ($)": 0.0}]
                save_portfolios(portfolios_db)
                st.success(f"สร้างโปรไฟล์ {new_profile_name} แล้ว! กรุณาเลือกจากแถบด้านซ้าย")
                st.rerun()
            elif new_profile_name in portfolios_db:
                st.warning("ชื่อนี้มีอยู่แล้วครับ")
                
    st.markdown("---")
    
    if selected_profile != "-- เลือกโปรไฟล์ --":
        st.markdown(f"#### 📊 2. จัดการพอร์ตการลงทุนของ: **{selected_profile}**")
        
        current_data = portfolios_db.get(selected_profile, [])
        if not current_data:
            current_data = [{"Ticker": "AAPL", "Current Value ($)": 0.0}]
            
        df_portfolio = pd.DataFrame(current_data)
        
        edited_portfolio = st.data_editor(
            df_portfolio,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Ticker": st.column_config.SelectboxColumn("Ticker", options=watchlist, required=True),
                "Current Value ($)": st.column_config.NumberColumn("มูลค่าปัจจุบัน ($)", min_value=0.0, format="$%.2f")
            }
        )
        
        if st.button("💾 บันทึกข้อมูลพอร์ต"):
            # Cleanup any empty rows or NaNs
            clean_data = edited_portfolio.dropna(subset=['Ticker']).to_dict('records')
            portfolios_db[selected_profile] = clean_data
            save_portfolios(portfolios_db)
            st.success("บันทึกข้อมูลพอร์ตเรียบร้อยแล้ว!")
            
        st.markdown("#### 🤖 3. ประมวลผลแผนสับเปลี่ยน (AI Rotation)")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            strategy = st.radio("เลือกกลยุทธ์การวิเคราะห์:", ["เกาะเทรนด์ (Trend Following)", "เล่นรอบสวิง (Swing Trade + BB)"], index=0)
        with col_opt2:
            max_new = st.slider("กระจายเงินไปซื้อหุ้นใหม่ไม่เกินกี่ตัว?", min_value=1, max_value=5, value=3)
            
        if st.button("🔄 วิเคราะห์แผนการสับเปลี่ยน"):
            with st.spinner("กำลังสแกนเปรียบเทียบความแข็งแกร่ง..."):
                strat_mode = "swing" if "Swing" in strategy else "trend"
                screener_df = screen_all_stocks(watchlist, period, strategy=strat_mode)
                # Pass the edited_portfolio explicitly to avoid needing to save first
                sell_holds, buys, freed_cash = generate_rotation_plan(edited_portfolio, screener_df, max_new_picks=max_new)
                
                
                # --- Sankey Diagram Logic ---
                sells = [item for item in sell_holds if "SELL" in item['Action']]
                holds = [item for item in sell_holds if "SELL" not in item['Action']]
                
                if sells or buys:
                    st.markdown("##### 🗺️ แผนผังการกระจายเงิน (Money Flow Mapping)")
                    
                    # Create nodes
                    node_labels = [f"🔴 ขาย: {s['Ticker']}" for s in sells]
                    node_colors = ["#ef4444"] * len(sells)
                    
                    cash_idx = len(node_labels)
                    node_labels.append(f"💰 กองทุนเงินสด<br>(${freed_cash:.2f})")
                    node_colors.append("#eab308")
                    
                    for b in buys:
                        node_labels.append(f"🟢 ซื้อ: {b['Ticker']}")
                        node_colors.append("#10b981")
                        
                    sources = []
                    targets = []
                    values = []
                    
                    # Sells -> Cash Pool
                    for i, s in enumerate(sells):
                        sources.append(i)
                        targets.append(cash_idx)
                        values.append(s['Amount'])
                        
                    # Cash Pool -> Buys
                    for j, b in enumerate(buys):
                        sources.append(cash_idx)
                        targets.append(cash_idx + 1 + j)
                        values.append(b['Amount'])
                        
                    # If cash is not fully allocated, create a hold cash node
                    allocated_cash = sum(b['Amount'] for b in buys)
                    leftover = freed_cash - allocated_cash
                    if leftover > 0.01:
                        hold_idx = len(node_labels)
                        node_labels.append(f"🔒 ถือเงินสดรอ<br>(${leftover:.2f})")
                        node_colors.append("#6b7280")
                        sources.append(cash_idx)
                        targets.append(hold_idx)
                        values.append(leftover)

                    # Only plot if there are flows
                    if sources:
                        fig = go.Figure(data=[go.Sankey(
                            valueformat = ".2f",
                            valuesuffix = " USD",
                            node = dict(
                              pad = 25,
                              thickness = 20,
                              line = dict(color = "rgba(255,255,255,0.1)", width = 1),
                              label = node_labels,
                              color = node_colors
                            ),
                            link = dict(
                              source = sources,
                              target = targets,
                              value = values,
                              color = "rgba(255, 255, 255, 0.15)"
                            )
                        )])
                        
                        fig.update_layout(
                            font=dict(size=14, family="Prompt", color="white"),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=20, l=0, r=0, b=20),
                            height=350
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # --- Text Summary ---
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("##### 🛒 1. หุ้นที่ต้องจัดการ (Action Required)")
                    if not sells and not buys:
                        st.info("ไม่มีแอคชั่นที่ต้องทำ พอร์ตสมดุลดีแล้ว")
                        
                    for item in sells:
                        st.error(f"{item['Action']} **{item['Ticker']}** | นำเงินออกมา **${item['Amount']:.2f}** | *{item['Reason']}*")
                        
                    if freed_cash > 0:
                        st.markdown(f"**💰 เงินสดที่เตรียมสับเปลี่ยน: ${freed_cash:.2f}**")
                        for item in buys:
                            st.success(f"{item['Action']} **{item['Ticker']}** | แบ่งเงินเข้าซื้อ **${item['Amount']:.2f}** | *{item['Reason']}*")
                
                with col_right:
                    st.markdown("##### 🛡️ 2. หุ้นที่ควรถือต่อ (Hold & Let Profit Run)")
                    if not holds:
                        st.info("ไม่มีหุ้นที่เข้าเกณฑ์ให้ถือต่อ")
                    for item in holds:
                        if "🟢" in item['Action']:
                            st.success(f"{item['Action']} **{item['Ticker']}** | ถือต่อไป **${item['Amount']:.2f}** | *{item['Reason']}*")
                        else:
                            st.warning(f"{item['Action']} **{item['Ticker']}** | รอดูสถานการณ์ **${item['Amount']:.2f}** | *{item['Reason']}*")

