import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_engine import get_stock_data, generate_trading_plan, analyze_signals, screen_all_stocks, allocate_funds, get_daily_alerts_and_news, generate_rotation_plan
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

st.set_page_config(page_title="Jarvis Terminal", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700;800&display=swap');

/* GLOBAL RESETS & FONTS */
html, body {
    color: #F8FAFC !important; /* Force white text globally */
}
p, h1, h2, h3, h4, h5, h6, label, li, a {
    font-family: 'Noto Sans Thai', sans-serif;
}
/* Specifically target dataframe headers and metric values */
[data-testid="stMetricValue"] {
    font-family: 'Noto Sans Thai', sans-serif !important;
    font-size: 36px !important;
    font-weight: 700 !important;
    color: #00FFA3 !important;
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
#MainMenu, footer {visibility: hidden;}
header {background: transparent !important;}

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
    color: #E2E8F0 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 36px !important;
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #FFF, #00FFA3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 4px 20px rgba(0,255,163,0.2);
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
    color: #FFFFFF !important;
    margin-bottom: 1.5rem !important;
}
/* Ensure captions and small text are bright enough */
small, .st-emotion-cache-1qg05tj, .st-emotion-cache-16idsys p {
    color: #E2E8F0 !important;
}

/* Mobile Adjustments (Phones) */
@media (max-width: 768px) {
    .block-container { padding-top: 1rem !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; }
}

/* Tablet Adjustments (iPads) */
@media (min-width: 769px) and (max-width: 1024px) {
    [data-testid="stMetricValue"] { font-size: 32px !important; }
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

/* SIDEBAR STYLING */
[data-testid="stSidebar"] {
    background-color: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebarNav"] {display: none;} /* Hide default nav if any */

/* Beautify Sidebar Radio Buttons */
.stRadio > div {
    gap: 15px;
}
.stRadio label {
    background: rgba(255,255,255,0.03);
    padding: 10px 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s ease;
    cursor: pointer;
}
.stRadio label:hover {
    background: rgba(255,255,255,0.1);
    transform: translateX(5px);
}
/* Ensure the text is visible */
.stRadio label div {
    font-weight: 600 !important;
    font-size: 15px !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='gradient-text'>FORECAST TRADING</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>AI QUANTITATIVE ANALYSIS & PORTFOLIO ROTATION</p>", unsafe_allow_html=True)

# ----------------- SIDEBAR MENU -----------------
with st.sidebar:
    st.markdown("### 🧭 MAIN MENU")
    menu = st.radio("เลือกหน้าต่างการทำงาน:", [
        "🌐 Market Overview", 
        "📈 AI Chart & Strategy", 
        "🔄 Portfolio Rotation"
    ])
    st.markdown("---")
    st.markdown("### ⚙️ SETTINGS")
    watchlist_input = st.text_area("รายการหุ้น (Watchlist)", value="AAPL, TSLA, NVDA, MSFT, AMZN, META, GOOGL, AMD, SHOP, NFLX")
    watchlist = [t.strip().upper() for t in watchlist_input.split(",") if t.strip()]
    period = st.selectbox("กรอบเวลา (Timeframe)", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

# ----------------- PAGE 1: MARKET OVERVIEW -----------------
if menu == "🌐 Market Overview":
    st.markdown("### 🌐 ศูนย์บัญชาการตลาด (Market Overview)")
    
    if st.button("📡 สแกนสถานะตลาดทั้งหมด (Scan Market)"):
        with st.spinner("กำลังเชื่อมต่อข้อมูลเรียลไทม์..."):
            screener_df = screen_all_stocks(watchlist, period)
            alerts, news_feed = get_daily_alerts_and_news(watchlist)
            
            # Top Split: Alerts (Left) / Good News (Right)
            col_alerts, col_news = st.columns(2)
            
            with col_alerts:
                st.markdown("#### 🚨 สัญญาณเตือนภัย (Volatility Alerts)")
                if alerts:
                    for alert in alerts:
                        if "🔴" in alert['Alert'] or "อันตราย" in alert['Alert']:
                            st.error(f"**[{alert['Ticker']}]** {alert['Alert']}")
                        else:
                            st.success(f"**[{alert['Ticker']}]** {alert['Alert']}")
                else:
                    st.info("ไม่มีสัญญาณเตือนรุนแรงในตลาด")
                    
                # Sell List Highlights
                sell_df = screener_df[screener_df['Score'] <= 0].copy()
                if not sell_df.empty:
                    st.warning("⚠️ **หุ้นอ่อนแอที่ควรหลีกเลี่ยง:** " + ", ".join(sell_df['Ticker'].tolist()))
            
            with col_news:
                st.markdown("#### 🟢 ข่าวสารเชิงบวก & โอกาส (Catalysts)")
                if news_feed:
                    for item in news_feed:
                        if item['Color'] == 'green':
                            st.success(f"[{item['Ticker']}] {item['Title']}")
                else:
                    st.info("ยังไม่มีปัจจัยบวกเด่นชัดในวันนี้")
                    
                # Buy List Highlights
                buy_df = screener_df[screener_df['Score'] >= 8].copy()
                if not buy_df.empty:
                    st.success("🎯 **หุ้นแนะนำเข้าซื้อ (Top Picks):** " + ", ".join(buy_df['Ticker'].tolist()))
                    
            st.markdown("---")
            st.markdown("#### 📊 ตารางสถานะความแข็งแกร่ง (Live Heatmap)")
            styled_all = screener_df[['Ticker', 'Price', 'RSI', 'Score', 'Status']].style.format(
                {'Price': '${:.2f}', 'RSI': '{:.1f}', 'Score': '{:.1f}'}
            )
            st.dataframe(styled_all, use_container_width=True)

# ----------------- PAGE 2: AI CHART & STRATEGY -----------------
elif menu == "📈 AI Chart & Strategy":
    st.markdown("### 📈 วิเคราะห์กราฟเชิงลึก (AI Chart & Strategy)")
    
    target_ticker = st.selectbox("เลือกหุ้นที่ต้องการวิเคราะห์เจาะลึก:", options=watchlist)
    
    if st.button("🧠 เริ่มวิเคราะห์ด้วย AI"):
        with st.spinner(f"กำลังดึงข้อมูลและคำนวณโมเดลสำหรับ {target_ticker}..."):
            df, info = get_stock_data(target_ticker, period)
            
            if df is None or df.empty:
                st.error("ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบชื่อหุ้น")
            else:
                latest_close = df['Close'].iloc[-1]
                res_val = df['Resistance'].iloc[-1]
                sup_val = df['Support'].iloc[-1]
                rsi_val = df['RSI'].iloc[-1]
                plan = generate_trading_plan(df)
                
                # Split Screen: Left (Chart 70%), Right (Metrics & Plan 30%)
                col_chart, col_plan = st.columns([7, 3])
                
                with col_chart:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
                    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='#f59e0b', width=2), name='SMA 50'))
                    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='#3b82f6', width=2), name='SMA 200'))
                    
                    # Bollinger Bands
                    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1), name='BB Upper', showlegend=False))
                    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)', name='Bollinger Bands'))
                    
                    fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], line=dict(color='#ef4444', width=1.5, dash='dash'), name='Resistance'))
                    fig.add_trace(go.Scatter(x=df.index, y=df['Support'], line=dict(color='#10b981', width=1.5, dash='dash'), name='Support'))
                    
                    if "error" not in plan and "action" in plan:
                        latest_date = df.index[-1]
                        if "BUY" in plan["action"]:
                            fig.add_annotation(x=latest_date, y=plan['buy_target'], text="🟢 BUY", showarrow=True, arrowhead=1, arrowcolor="#10b981")
                            fig.add_annotation(x=latest_date, y=plan['sell_target'], text="🎯 TARGET", showarrow=True, arrowhead=1, arrowcolor="#3b82f6")
                        
                    fig.update_layout(
                        title=f"{target_ticker} - Technical Analysis",
                        template='plotly_dark',
                        xaxis_rangeslider_visible=False,
                        height=550,
                        margin=dict(l=0, r=0, t=50, b=0),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_plan:
                    st.metric("ราคาปัจจุบัน (Price)", f"${latest_close:.2f}")
                    st.metric("RSI (ความร้อนแรง)", f"{rsi_val:.1f}")
                    st.metric("แนวต้าน (Resistance)", f"${res_val:.2f}" if pd.notna(res_val) else "N/A")
                    st.metric("จุดคัทลอส (Support)", f"${sup_val:.2f}" if pd.notna(sup_val) else "N/A")
                    
                    st.markdown("---")
                    
                    if "error" in plan:
                        st.warning(f"❌ {plan.get('error', 'Error')}")
                    else:
                        st.markdown("#### 🤖 AI Action")
                        action_str = plan.get('action', '')
                        if 'BUY' in action_str:
                            st.success(f"**{action_str}**\n\n*{plan.get('reason', '')}*")
                        elif 'SELL' in action_str:
                            st.error(f"**{action_str}**\n\n*{plan.get('reason', '')}*")
                        else:
                            st.info(f"**{action_str}**\n\n*{plan.get('reason', '')}*")
                            
                        if "buy_target" in plan:
                            b_target = plan.get('buy_target')
                            s_target = plan.get('sell_target')
                            c_loss = plan.get('cut_loss')
                            
                            if b_target is not None:
                                st.markdown(f"**เป้าเข้าซื้อ (Buy Target):** ${b_target:.2f}")
                            if s_target is not None:
                                st.markdown(f"**เป้าขายทำกำไร (Take Profit):** ${s_target:.2f}")
                            if c_loss is not None:
                                st.markdown(f"**จุดตัดขาดทุน (Cut Loss):** ${c_loss:.2f}")
                            
                            if b_target is not None and c_loss is not None and s_target is not None:
                                risk = b_target - c_loss
                                reward = s_target - b_target
                                if risk > 0 and reward > 0:
                                    rr_ratio = reward / risk
                                    if rr_ratio >= 2:
                                        st.caption(f"✅ ความคุ้มค่า: ดีมาก (R/R 1:{rr_ratio:.2f})")
                                    else:
                                        st.caption(f"⚠️ ความคุ้มค่า: ปานกลาง (R/R 1:{rr_ratio:.2f})")

# ----------------- PAGE 3: PORTFOLIO ROTATION -----------------
elif menu == "🔄 Portfolio Rotation":
    st.markdown("### 🔄 ระบบสับเปลี่ยนพอร์ตอัจฉริยะ (Smart Rotation)")
    
    portfolios_db = load_portfolios()
    
    # Split Screen: Left (Input 40%), Right (Output 60%)
    col_input, col_output = st.columns([4, 6])
    
    with col_input:
        st.markdown("#### 💼 1. ข้อมูลพอร์ตของคุณ")
        profile_names = list(portfolios_db.keys())
        selected_profile = st.selectbox("เลือกโปรไฟล์พอร์ต:", ["+ สร้างโปรไฟล์ใหม่..."] + profile_names)
        
        if selected_profile == "+ สร้างโปรไฟล์ใหม่...":
            new_prof = st.text_input("ตั้งชื่อโปรไฟล์ใหม่ (เช่น พอร์ตเทรดสั้น, พอร์ตวีไอ):")
            if new_prof:
                selected_profile = new_prof
        
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
            clean_data = edited_portfolio.dropna(subset=['Ticker']).to_dict('records')
            portfolios_db[selected_profile] = clean_data
            save_portfolios(portfolios_db)
            st.success("บันทึกเรียบร้อย!")
            
        st.markdown("---")
        st.markdown("#### ⚙️ 2. ตั้งค่าการวิเคราะห์")
        strategy = st.radio("เลือกกลยุทธ์:", ["เกาะเทรนด์ (Trend Following)", "เล่นรอบสวิง (Swing Trade + BB)"], index=0)
        max_new = st.slider("กระจายเงินซื้อหุ้นใหม่ไม่เกินกี่ตัว?", min_value=1, max_value=5, value=3)
        calc_btn = st.button("🔄 เริ่มวิเคราะห์สับเปลี่ยน")
        
    with col_output:
        st.markdown("#### 🗺️ 3. แผนผังการกระจายเงิน (Money Flow)")
        if calc_btn:
            with st.spinner("AI กำลังคำนวณเส้นทางกระแสเงิน..."):
                strat_mode = "swing" if "Swing" in strategy else "trend"
                screener_df = screen_all_stocks(watchlist, period, strategy=strat_mode)
                sell_holds, buys, freed_cash = generate_rotation_plan(edited_portfolio, screener_df, max_new_picks=max_new)
                
                sells = [item for item in sell_holds if "SELL" in item['Action']]
                holds = [item for item in sell_holds if "SELL" not in item['Action']]
                
                if sells or buys:
                    # Create nodes
                    node_labels = [f"🔴 ขาย: {s['Ticker']}" for s in sells]
                    node_colors = ["#ef4444"] * len(sells)
                    
                    cash_idx = len(node_labels)
                    node_labels.append(f"💰 เงินสด<br>(${freed_cash:.2f})")
                    node_colors.append("#eab308")
                    
                    for b in buys:
                        node_labels.append(f"🟢 ซื้อ: {b['Ticker']}")
                        node_colors.append("#10b981")
                        
                    sources = []
                    targets = []
                    values = []
                    
                    for i, s in enumerate(sells):
                        sources.append(i)
                        targets.append(cash_idx)
                        values.append(s['Amount'])
                        
                    for j, b in enumerate(buys):
                        sources.append(cash_idx)
                        targets.append(cash_idx + 1 + j)
                        values.append(b['Amount'])
                        
                    allocated_cash = sum(b['Amount'] for b in buys)
                    leftover = freed_cash - allocated_cash
                    if leftover > 0.01:
                        hold_idx = len(node_labels)
                        node_labels.append(f"🔒 ถือเงินสดรอ<br>(${leftover:.2f})")
                        node_colors.append("#6b7280")
                        sources.append(cash_idx)
                        targets.append(hold_idx)
                        values.append(leftover)

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
                            font=dict(size=14, family="Noto Sans Thai", color="white"),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, l=0, r=0, b=10),
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Summary List below Sankey
                c1, c2 = st.columns(2)
                with c1:
                    if sells:
                        for item in sells:
                            st.error(f"🔴 ขาย **{item['Ticker']}** | เอากำไร/ตัดจบ **${item['Amount']:.2f}**")
                    if buys:
                        for item in buys:
                            st.success(f"🟢 เข้าซื้อ **{item['Ticker']}** | **${item['Amount']:.2f}**")
                with c2:
                    if holds:
                        for item in holds:
                            if "🟢" in item['Action']:
                                st.success(f"🛡️ ถือต่อ **{item['Ticker']}** | แข็งแกร่ง")
                            else:
                                st.warning(f"⏳ รอดู **{item['Ticker']}** | พักตัว")
        else:
            st.info("👈 กดปุ่ม 'เริ่มวิเคราะห์สับเปลี่ยน' ด้านซ้ายมือ เพื่อดูแผนผังการไหลของเงิน")
