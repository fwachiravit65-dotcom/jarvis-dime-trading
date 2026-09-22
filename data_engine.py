import yfinance as yf
import pandas as pd
import ta

def get_stock_data(ticker, period="1y"):
    """Fetch historical data and calculate technical indicators."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None
            
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        # 1. Moving Averages
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        
        # 2. RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # 3. MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # 4. Support and Resistance (20-day lookback)
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        info = stock.info
        return df, info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

def analyze_signals(df):
    """Generate basic rule-based signals."""
    if df is None or df.empty:
        return ["No Data"]
        
    latest = df.iloc[-1]
    signals = []
    
    if pd.notna(latest['RSI']):
        if latest['RSI'] > 70:
            signals.append("🔴 RSI > 70 (Overbought): ราคาสูงเกินไป ระวังการย่อตัว/พิจารณา Take Profit")
        elif latest['RSI'] < 30:
            signals.append("🟢 RSI < 30 (Oversold): ราคาต่ำเกินไป อาจเป็นจุดเข้าสะสมที่ดี")
        else:
            signals.append("🟡 RSI ปกติ: ราคาแกว่งตัวในกรอบ (Wait & See)")
            
    if pd.notna(latest['SMA_50']) and pd.notna(latest['Close']):
        if latest['Close'] > latest['SMA_50']:
            signals.append("🟢 ราคาอยู่เหนือเส้น SMA 50: แนวโน้มระยะสั้นเป็นขาขึ้น")
        else:
            signals.append("🔴 ราคาอยู่ต่ำกว่าเส้น SMA 50: แนวโน้มระยะสั้นเป็นขาลง หรือกำลังพักตัว")
            
    return signals

def generate_trading_plan(df):
    """Generate a concrete trading action plan based on current data."""
    if df is None or df.empty:
        return None
        
    latest = df.iloc[-1]
    current_price = latest['Close']
    
    # Extract calculated S/R
    support = latest['Support']
    resistance = latest['Resistance']
    rsi = latest['RSI']
    sma50 = latest['SMA_50']
    sma200 = latest['SMA_200']
    
    plan = {
        "action": "",
        "reason": "",
        "buy_target": None,
        "sell_target": None,
        "cut_loss": None
    }
    
    # Action Logic
    if pd.isna(rsi) or pd.isna(support) or pd.isna(resistance):
        plan['action'] = "⚠️ ข้อมูลไม่เพียงพอ"
        plan['reason'] = "รอข้อมูลอัปเดต"
        plan['immediate'] = {
            "current_price": current_price,
            "buy_target": current_price,
            "buy_cut_loss": current_price,
        }
        return plan

    if rsi < 40 and current_price > sma200:
        plan['action'] = "🟢 BUY (แนะนำให้เข้าซื้อ)"
        plan['reason'] = "ราคาอยู่ในแนวโน้มขาขึ้นระยะยาว (เหนือ SMA 200) แต่มีการย่อตัวลงมาจน RSI ต่ำ ถือเป็นจุดสะสมที่ดี"
        plan['buy_target'] = current_price
        plan['sell_target'] = resistance
        plan['cut_loss'] = support * 0.98 # เผื่อหลุดแนวรับ 2%
        
    elif rsi > 70:
        plan['action'] = "🔴 SELL (พิจารณาเทขายหลบพักตัว)"
        plan['reason'] = "RSI ทะลุ 70 (Overbought) ราคาพุ่งแรงเกินไปในระยะสั้น มีความเสี่ยงที่จะโดนเทขายทำกำไรสูง"
        plan['buy_target'] = sma50 # จุดรับของกลับคืน
        plan['sell_target'] = current_price
        plan['cut_loss'] = None
        
    else:
        plan['action'] = "🟡 WAIT (ถือรอ / ชะลอการซื้อ)"
        plan['reason'] = "ราคาอยู่กลางกรอบ ควรรอให้ราคาตกมาใกล้แนวรับ หรือทะลุแนวต้านก่อน"
        plan['buy_target'] = support
        plan['sell_target'] = resistance
        plan['cut_loss'] = support * 0.98

    # Add immediate action scenario
    plan['immediate'] = {
        "current_price": current_price,
        "buy_target": resistance,
        "buy_cut_loss": support * 0.98,
    }

    return plan

def screen_all_stocks(tickers, period="1y"):
    """Scan multiple stocks and score them based on technicals."""
    results = []
    for ticker in tickers:
        df, info = get_stock_data(ticker, period)
        if df is None or df.empty:
            continue
            
        latest = df.iloc[-1]
        current_price = latest['Close']
        rsi = latest['RSI']
        sma50 = latest['SMA_50']
        sma200 = latest['SMA_200']
        
        status = "🟡 แกว่งตัวพักฐาน (Wait)"
        score = 0
        
        if pd.isna(rsi) or pd.isna(sma200):
            continue
            
        if current_price > sma200:
            if rsi < 45: 
                status = "🟢 ย่อตัวน่าเก็บ (Buy the Dip)"
                score = 10 # คะแนนเต็ม น่าเก็บที่สุด
            elif rsi > 70:
                status = "🔴 ขึ้นแรงไป (Overbought)"
                score = 0
            elif current_price > sma50:
                status = "🟢 แนวโน้มแกร่ง (Strong Momentum)"
                # ยิ่ง RSI ต่ำ (ห่างจาก 70) ยิ่งมีพื้นที่ให้วิ่งเยอะ = คะแนนเยอะ (ช่วงคะแนนประมาณ 5-9)
                score = 5 + ((70 - rsi) / 10) 
            else:
                status = "🟡 พักตัวในขาขึ้น (Wait & See)"
                score = 3
        else:
            if rsi < 30:
                status = "🟡 ลงลึก (Oversold - เสี่ยงสวนเทรนด์)"
                score = 1
            else:
                status = "🔴 ขาลง (Avoid/Wait)"
                score = -2
                
        results.append({
            "Ticker": ticker,
            "Price": current_price,
            "RSI": rsi,
            "Status": status,
            "Score": score
        })
    return pd.DataFrame(results)

def allocate_funds(screener_df, amount):
    """Allocate funds based on screener scores."""
    # เลือกเฉพาะตัวที่คะแนน >= 5 (แนวโน้มแกร่ง หรือ น่าเก็บ)
    buy_candidates = screener_df[screener_df['Score'] >= 5].sort_values(by='Score', ascending=False)
    
    if buy_candidates.empty:
        return "⚠️ หุ้นใน Watchlist ตอนนี้ไม่มีตัวไหนอยู่ในจุดเข้าซื้อที่ปลอดภัย (แพงไปหรือเป็นขาลง) แนะนำให้ถือเงินสด (Hold Cash) รอจังหวะย่อตัวครับ", pd.DataFrame()
        
    # ปลดล็อคจาก 3 ตัว เป็นสูงสุด 5 ตัว เพื่อกระจายความเสี่ยงให้ครอบคลุม
    top_picks = buy_candidates.head(5).copy()
    
    # คำนวณสัดส่วนเงินตามความแข็งแกร่ง (Weighted Allocation)
    total_score = top_picks['Score'].sum()
    top_picks['Allocation ($)'] = (top_picks['Score'] / total_score) * amount
    
    num_picks = len(top_picks)
    return f"✅ ระบบพบหุ้นแข็งแกร่ง {num_picks} ตัว (ยิ่งกราฟสวย/ย่อตัวน่าเก็บ จะยิ่งได้รับการแบ่งเงินทุนสัดส่วนมากขึ้น):", top_picks
