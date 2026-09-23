import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta
import yfinance as yf
from data_engine import get_stock_data, analyze_signals, generate_trading_plan, screen_all_stocks, allocate_funds, get_daily_alerts_and_news, check_emergency_alerts

st.set_page_config(page_title="Jarvis Terminal", layout="wide", page_icon="⚡", initial_sidebar_state="expanded")

# ... (CSS stays the same, I'll search for the header to insert the banner)


custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Prompt', sans-serif !important;
}

/* Remove top padding for a full-screen app feel */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 0rem !important;
    max-width: 95% !important;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Modern Glassmorphism Metric Cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 15px 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Make metric labels softer */
[data-testid="stMetricLabel"] {
    font-size: 14px !important;
    color: #a3a8b8 !important;
    font-weight: 500 !important;
}
/* Make metric values massive */
[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 700 !important;
}

/* Modern Glowing Buttons */
.stButton > button {
    background: linear-gradient(90deg, #ff4b4b 0%, #ff2a2a 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
    transition: all 0.3s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6) !important;
    background: linear-gradient(90deg, #ff2a2a 0%, #ff0000 100%) !important;
}

/* Sleek Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 6px;
    gap: 10px;
    margin-bottom: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 12px 24px;
    border: none !important;
    background-color: transparent;
    transition: background-color 0.2s;
    font-size: 16px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(255,255,255,0.12) !important;
    color: white !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(15, 17, 22, 0.98);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Headers */
h1 {
    font-weight: 700 !important;
    background: -webkit-linear-gradient(45deg, #fff, #a3a8b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* 📱 Mobile Responsiveness */
@media (max-width: 768px) {
    .block-container {
        padding-top: 2rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* ย่อขนาดตัวอักษรลงในมือถือ */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    h1 {
        font-size: 26px !important;
    }
    
    /* ทำให้แท็บเลื่อนซ้ายขวาได้ ไม่เบียดกัน */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        white-space: nowrap;
        padding: 5px;
        gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        font-size: 14px;
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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


tab1, tab2, tab3 = st.tabs(["📈 วางแผนเทรด (Trade)", "💼 สแกนพอร์ต (Portfolio)", "🚨 เรดาร์ตลาด (Radar)"])

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
                st.dataframe(sell_df[['Ticker', 'Price', 'RSI', 'Status']].style.format({'Price': '${:.2f}', 'RSI': '{:.1f}'}), use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📊 อัปเดตสถานะหุ้นทั้งหมด (Live Market Status)")
            st.dataframe(screener_df[['Ticker', 'Price', 'RSI', 'Status']].style.format({'Price': '${:.2f}', 'RSI': '{:.1f}'}), use_container_width=True)


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
