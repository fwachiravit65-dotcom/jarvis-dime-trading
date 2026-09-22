import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from data_engine import get_stock_data, analyze_signals, generate_trading_plan, screen_all_stocks, allocate_funds, get_daily_alerts_and_news

st.set_page_config(page_title="Jarvis Trading Center", layout="wide", page_icon="🤖")
st.title("🤖 Jarvis Command Center")

watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "RGTI", "RKLB", "SHOP", "JEPQ", "AMD", "TSM"]

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("📊 ตั้งค่าข้อมูล")
    selected_ticker = st.selectbox("เลือกหุ้นเพื่อเจาะลึก (Single Stock):", watchlist)
    custom_ticker = st.text_input("หรือพิมพ์ชื่อหุ้นตัวอื่น (e.g. NFLX):").upper()
    if custom_ticker:
        selected_ticker = custom_ticker
        
    period = st.selectbox("กรอบเวลาย้อนหลัง (Timeframe):", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

# Create Tabs
tab1, tab2, tab3 = st.tabs(["🔍 เจาะลึกรายตัว (Single Stock)", "💼 จัดพอร์ต & สแกนหุ้น (Money Management)", "📰 ข่าวสาร & เรดาร์ความผันผวน (Daily News)"])

@st.cache_data(ttl=3600)
def load_data(ticker, period):
    return get_stock_data(ticker, period)

# --- TAB 1: Single Stock Analysis ---
with tab1:
    with st.spinner(f"กำลังดึงข้อมูลและคำนวณแผนสำหรับ {selected_ticker}..."):
        df, info = load_data(selected_ticker, period)

    if df is None or df.empty:
        st.error(f"ไม่พบข้อมูลสำหรับหุ้น {selected_ticker} กรุณาตรวจสอบชื่อย่ออีกครั้ง")
    else:
        col1, col2 = st.columns([2, 1.2])
        with col1:
            st.subheader(f"📈 {selected_ticker} - Technical Chart")
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2])
                                
            # 1. Candlestick and MAs
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='blue', width=1), name='SMA 200'), row=1, col=1)
            
            # Support and Resistance Lines
            fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='rgba(255, 99, 71, 0.7)', width=2, dash='dot'), name='Resistance (20D)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='rgba(60, 179, 113, 0.7)', width=2, dash='dot'), name='Support (20D)'), row=1, col=1)
            
            # 2. Volume
            colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
            
            # 3. RSI
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            fig.update_layout(height=800, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("🏢 ข้อมูลปัจจุบัน (Current Status)")
            # Use reliable Close price from DataFrame instead of flaky info dict
            latest_close = df['Close'].iloc[-1]
            st.metric("Current Price", f"${latest_close:.2f}")
                
            st.subheader("🚦 สัญญาณทางเทคนิค")
            signals = analyze_signals(df)
            for sig in signals:
                st.info(sig)
                
            st.markdown("---")
            st.subheader("🎯 แผนการเทรด (Action Plan)")
            st.caption("คลิกปุ่มด้านล่างเพื่อคำนวณแผนการเข้าซื้อ/ขาย จากข้อมูลกราฟล่าสุด")
            
            if st.button("⚡ สร้างแผนการเทรด (Generate Plan)", type="primary", use_container_width=True):
                plan = generate_trading_plan(df)
                if plan:
                    st.markdown(f"### {plan['action']}")
                    st.write(f"**เหตุผล:** {plan['reason']}")
                    
                    st.markdown("#### รายละเอียดตัวเลข:")
                    p_col1, p_col2 = st.columns(2)
                    
                    with p_col1:
                        st.metric("📍 จุดเข้าซื้อ (Buy Target)", f"${plan['buy_target']:.2f}" if plan['buy_target'] else "N/A")
                        st.metric("🛑 จุดยอมแพ้ (Cut Loss)", f"${plan['cut_loss']:.2f}" if plan['cut_loss'] else "N/A")
                        
                    with p_col2:
                        st.metric("💰 จุดทำกำไร (Sell Target)", f"${plan['sell_target']:.2f}" if plan['sell_target'] else "N/A")
                        
                    if plan['buy_target'] and plan['sell_target'] and plan['cut_loss'] and plan['buy_target'] > plan['cut_loss']:
                        risk = plan['buy_target'] - plan['cut_loss']
                        reward = plan['sell_target'] - plan['buy_target']
                        if risk > 0 and reward > 0:
                            rr_ratio = reward / risk
                            st.write(f"**อัตราส่วน Risk/Reward (กรณีรอจุดเข้า):** 1 : {rr_ratio:.2f}")
                            if rr_ratio >= 2:
                                st.success("✅ ความคุ้มค่าสูง: กำไรมากกว่าความเสี่ยง 2 เท่าขึ้นไป")
                            else:
                                st.warning("⚠️ ความคุ้มค่าปานกลาง/ต่ำ: ควรระมัดระวังในการเข้าซื้อ")
                    
                    st.markdown("---")
                    st.markdown("#### ⚡ กรณีต้องการซื้อ/ขาย ณ ราคาปัจจุบัน (Immediate Action)")
                    st.caption("ข้อมูลสำหรับกรณีที่คุณไม่อยากรอกราฟย่อตัว/เบรกเอาท์ และต้องการกดคำสั่งในแอป Dime ทันทีตอนนี้")
                    
                    imm_col1, imm_col2 = st.columns(2)
                    with imm_col1:
                        st.info(f"**🛒 หากกด 'ซื้อ' ทันที (Buy Now)**\n\n"
                                f"จะได้ราคาต้นทุนประมาณ: **${plan['immediate']['current_price']:.2f}**\n\n"
                                f"🎯 เป้าขาย (Resistance): **${plan['immediate']['buy_target']:.2f}**\n\n"
                                f"🛑 จุดหนีตาย (Cut Loss): **${plan['immediate']['buy_cut_loss']:.2f}**")
                    with imm_col2:
                        st.warning(f"**💰 หากกด 'ขาย' ทันที (Sell Now)**\n\n"
                                   f"จะขายได้เงินที่ราคาประมาณ: **${plan['immediate']['current_price']:.2f}**\n\n"
                                   f"*(ใช้ในกรณีที่คุณมีของอยู่แล้ว และต้องการล็อกกำไร หรือหนีตาย ณ ราคาตลาดปัจจุบัน)*")

# --- TAB 2: Money Management & Screener ---
with tab2:
    st.header("💼 ระบบจัดสรรเงินทุน (Money Management & Stock Screener)")
    st.markdown("ระบบจะสแกนกราฟของหุ้นใน Watchlist ทั้งหมดพร้อมกัน เพื่อหาตัวที่กำลัง **ย่อตัวเสร็จแล้ว** หรือ **แนวโน้มแข็งแกร่งที่สุด** และแบ่งเงินลงทุนให้เหมาะสม")
    
    invest_amount = st.number_input("ใส่จำนวนเงินที่คุณต้องการเติมเข้าพอร์ตรอบนี้ (USD):", min_value=1.0, value=100.0, step=10.0)
    
    if st.button("🚀 สแกนตลาดและจัดสรรเงิน", type="primary"):
        with st.spinner("กำลังสแกนข้อมูล Watchlist... อาจใช้เวลาสักครู่"):
            screener_df = screen_all_stocks(watchlist, period)
            
            st.subheader("📊 สถานะหุ้นทั้งหมดตอนนี้")
            st.dataframe(screener_df[['Ticker', 'Price', 'RSI', 'Status']].style.format({'Price': '${:.2f}', 'RSI': '{:.1f}'}), use_container_width=True)
            
            st.markdown("---")
            st.subheader("💰 คำแนะนำการแบ่งเงิน (Allocation Plan)")
            msg, alloc_df = allocate_funds(screener_df, invest_amount)
            st.info(msg)
            
            if not alloc_df.empty:
                a_col1, a_col2 = st.columns([1, 1])
                with a_col1:
                    st.dataframe(alloc_df[['Ticker', 'Status', 'Allocation ($)']].style.format({'Allocation ($)': '${:.2f}'}), use_container_width=True)
                with a_col2:
                    fig_pie = px.pie(alloc_df, values='Allocation ($)', names='Ticker', title="สัดส่วนการกระจายเงิน")
                    st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 3: Daily News & Alerts ---
with tab3:
    st.header("📰 ข่าวสาร & เรดาร์จับการสวิง (Daily News & Alerts)")
    st.markdown("หน้านี้จะอัปเดตความเคลื่อนไหวรายวัน ว่ามีหุ้นตัวไหนสวิงแรงผิดปกติ และแสดงพาดหัวข่าวล่าสุดให้คุณติดตามครับ")
    
    if st.button("📡 ตรวจสอบเรดาร์ตลาดวันนี้ (Refresh Radar)", type="primary", use_container_width=True):
        with st.spinner("กำลังกวาดสัญญาณความผันผวนและพาดหัวข่าวจากตลาดโลก (อาจใช้เวลา 1-2 นาที)..."):
            alerts, news_feed = get_daily_alerts_and_news(watchlist)
            
            st.subheader("🚨 เรดาร์จับความผันผวน (Volatility Alerts)")
            st.caption("ระบบคำนวณจากระยะการแกว่งตัว (ATR) และโมเมนตัม (MACD) ของวันนี้เทียบกับค่าเฉลี่ยในอดีต")
            if alerts:
                for alert in alerts:
                    if "สวิงลง" in alert['Alert'] or "ลบกดดัน" in alert['Alert']:
                        st.error(f"**[{alert['Ticker']}]** {alert['Alert']} - {alert['Details']}")
                    else:
                        st.success(f"**[{alert['Ticker']}]** {alert['Alert']} - {alert['Details']}")
            else:
                st.info("✅ วันนี้ตลาดยังสงบ ไม่มีหุ้นตัวไหนในพอร์ตสวิงแรงผิดปกติให้ต้องกังวลครับ")
                
            st.markdown("---")
            st.subheader("🗞️ สแกนพาดหัวข่าวล่าสุด (News Sentiment Radar)")
            st.caption("ระบบใช้ Keyword Analysis ตรวจจับคำศัพท์ในข่าวเพื่อประเมินความเสี่ยงและทิศทางเบื้องต้น คลิกที่พาดหัวเพื่ออ่านเต็ม (ภาษาอังกฤษ)")
            
            if news_feed:
                for item in news_feed:
                    if item['Color'] == 'green':
                        st.success(f"**[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*\n\n(โดย {item['Publisher']})")
                    elif item['Color'] == 'red':
                        st.error(f"**[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*\n\n(โดย {item['Publisher']})")
                    else:
                        st.info(f"**[{item['Ticker']}] {item['Sentiment']}**\n\n**[{item['Title']}]({item['Link']})**\n\n*{item['Summary']}*\n\n(โดย {item['Publisher']})")
            else:
                st.write("ไม่มีข่าวสารอัปเดตในขณะนี้")
