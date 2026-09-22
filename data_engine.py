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

def get_daily_alerts_and_news(tickers):
    """Fetch volatility alerts and news, filtering news to match actual price momentum."""
    alerts = []
    news_feed = []
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        momentum_dir = 0 # 1=UP, -1=DOWN, 0=FLAT
        
        # 1. Calculate Volatility & Momentum Alert
        try:
            df = stock.history(period="3mo")
            if not df.empty and len(df) > 20:
                atr_obj = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
                df['ATR'] = atr_obj.average_true_range()
                
                macd = ta.trend.MACD(df['Close'])
                macd_hist = macd.macd_diff().iloc[-1]
                
                today_range = df['High'].iloc[-1] - df['Low'].iloc[-1]
                avg_atr = df['ATR'].iloc[-2]
                
                if pd.notna(avg_atr) and avg_atr > 0:
                    if today_range > 1.5 * avg_atr:
                        if df['Close'].iloc[-1] > df['Open'].iloc[-1]:
                            alerts.append({"Ticker": ticker, "Alert": "🔥 สวิงขึ้นรุนแรง (Bullish Volatility)", "Details": "ราคาแกว่งตัวกว้างกว่าปกติ มีแรงซื้อหนาแน่น โอกาสทะลุแนวต้านสูง"})
                            momentum_dir = 1
                        else:
                            alerts.append({"Ticker": ticker, "Alert": "⚠️ สวิงลงรุนแรง (Bearish Volatility)", "Details": "โดนเทขายหนักกว่าปกติ ทิศทางอันตราย ระวังหลุดแนวรับ"})
                            momentum_dir = -1
                    elif abs(macd_hist) > (df['Close'].iloc[-1] * 0.01): 
                         if macd_hist > 0:
                             alerts.append({"Ticker": ticker, "Alert": "🚀 โมเมนตัมบวกพุ่ง (Strong Upward Momentum)", "Details": "แรงซื้ออัดแน่นระยะสั้น กราฟสวย มีโอกาสพุ่งไปต่อ"})
                             momentum_dir = 1
                         else:
                             alerts.append({"Ticker": ticker, "Alert": "📉 โมเมนตัมลบกดดัน (Strong Downward Momentum)", "Details": "แรงขายหนาแน่นระยะสั้น ระวังราคาร่วงต่อเนื่อง ไม่ควรรีบรับ"})
                             momentum_dir = -1
        except Exception:
            pass

        # 2. Fetch News and Filter out contradictions
        try:
            news = stock.news
            if news:
                best_news = None
                for item in news:
                    content = item.get('content', {})
                    if not content:
                        continue
                        
                    title = content.get('title', 'No Title')
                    summary = content.get('summary', '')
                    publisher = content.get('provider', {}).get('displayName', 'Unknown')
                    link = (content.get('clickThroughUrl') or content.get('canonicalUrl') or {}).get('url', '#')
                    
                    text_to_check = (title + " " + summary).lower()
                    
                    pos_words = ['jump', 'surge', 'boost', 'beat', 'raise', 'upgrade', 'buy', 'strong', 'gain', 'top', 'bull', 'rally', 'advantage', 'lead']
                    neg_words = ['drop', 'fall', 'miss', 'downgrade', 'sell', 'weak', 'risk', 'skid', 'threat', 'warn', 'dip', 'bear', 'challenge', 'lower', 'fear']
                    
                    sentiment = "neutral"
                    # ป้องกันการแปลผิด เช่น 'sell-off is overdone' (แปลว่าลงมากไปแล้ว กำลังจะขึ้น)
                    if any(w in text_to_check for w in pos_words) or ("overdone" in text_to_check and "sell" in text_to_check):
                        sentiment = "positive"
                    elif any(w in text_to_check for w in neg_words):
                        sentiment = "negative"
                        
                    # ไส้กรองเวทมนตร์ (Magic Filter): เอาเฉพาะข่าวที่ "สอดคล้องกับกราฟจริง" หรือเป็นข่าวใหญ่จริงๆ
                    is_match = False
                    
                    if momentum_dir == 1 and sentiment == "positive":
                        is_match = True # กราฟพุ่ง + ข่าวดี = ของแท้
                    elif momentum_dir == -1 and sentiment == "negative":
                        is_match = True # กราฟร่วง + ข่าวร้าย = ของแท้
                    elif momentum_dir == 0 and sentiment != "neutral":
                        is_match = True # กราฟนิ่งๆ แต่มีข่าวใหญ่ (แง่บวก/ลบ) = น่าติดตาม
                        
                    if is_match:
                        # ได้ข่าวเด็ดที่ตรงกับกราฟแล้ว! เก็บข่าวนี้ข่าวเดียวพอ เพื่อไม่ให้รก
                        best_news = {
                            "Ticker": ticker,
                            "Title": title,
                            "Summary": summary[:150] + "..." if len(summary) > 150 else summary,
                            "Publisher": publisher,
                            "Link": link,
                            "Sentiment": "🌟 ข่าวดีดันราคา (Bullish Catalyst)" if sentiment == "positive" else "🚨 ข่าวร้ายกดดัน (Bearish Catalyst)",
                            "Color": "green" if sentiment == "positive" else "red"
                        }
                        break # เจอข่าวเด็ด 1 อันแล้ว ข้ามไปทำหุ้นตัวต่อไปเลย
                        
                if best_news:
                    news_feed.append(best_news)
        except Exception:
            pass

    return alerts, news_feed
