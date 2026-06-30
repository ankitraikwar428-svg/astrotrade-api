from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import swisseph as swe
from datetime import datetime
import pandas as pd
import requests

app = FastAPI(title="AstroTrade API - PRO Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "AstroTrade API PRO is running live! 🚀"}

def calculate_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

@app.get("/api/analyze_stock")
def analyze_stock(symbol: str = "RELIANCE.NS"):
    try:
        # Anti-Ban System (Bypassing Yahoo Finance Rate Limits)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # 1. TECHNICAL ANALYSIS
        stock = yf.Ticker(symbol, session=session)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return {"error": f"स्टॉक '{symbol}' का डेटा नहीं मिला। कृपया सही नाम डालें।"}
            
        current_price = round(hist['Close'].iloc[-1], 2)
        
        recent_hist = hist.tail(30)
        high = recent_hist['High'].max()
        low = recent_hist['Low'].min()
        pivot = (high + low + current_price) / 3
        s1 = round((2 * pivot) - high, 2)
        r1 = round((2 * pivot) - low, 2)
        s2 = round(pivot - (high - low), 2)
        r2 = round(pivot + (high - low), 2)

        hist['RSI'] = calculate_rsi(hist['Close'])
        macd, macd_signal = calculate_macd(hist['Close'])
        current_rsi = round(hist['RSI'].iloc[-1], 2)
        
        # New Smart Logic
        is_bullish = False
        tech_trend = "Neutral"
        if current_rsi < 30 and macd.iloc[-1] > macd_signal.iloc[-1]:
            tech_trend = "Strong Buy (RSI Oversold + MACD Crossover)"
            is_bullish = True
        elif current_rsi > 70:
            tech_trend = "Sell (RSI Overbought)"
        elif current_price > hist['Close'].mean():
            tech_trend = "Bullish Uptrend (Positive Momentum)"
            is_bullish = True
        else:
            tech_trend = "Bearish Downtrend (Negative Momentum)"

        # 2. ADVANCED ASTROLOGY
        swe.set_ephe_path('')
        now = datetime.utcnow()
        julday = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
        
        moon_pos, _ = swe.calc_ut(julday, swe.MOON)
        moon_degree = round(moon_pos[0], 2)
        
        nakshatra_idx = int(moon_degree / (360 / 27))
        nakshatras = ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वा भाद्रपद", "उत्तरा भाद्रपद", "रेवती"]
        current_nakshatra = nakshatras[nakshatra_idx]

        jupiter_pos, _ = swe.calc_ut(julday, swe.JUPITER)
        jupiter_degree = round(jupiter_pos[0], 2)

        astro_comment = f"चंद्रमा अभी '{current_nakshatra}' नक्षत्र में है। "
        if "पुष्य" in current_nakshatra or "अनुराधा" in current_nakshatra or "स्वाति" in current_nakshatra:
            astro_comment += "यह शेयर बाज़ार और निवेश के लिए बहुत ही शुभ नक्षत्र है (Wealth Yoga)! "
        
        angle_diff = abs(moon_degree - jupiter_degree)
        if 110 < angle_diff < 130 or angle_diff < 10:
            astro_comment += "चार्ट में गुरु (Jupiter) का शानदार गजकेसरी योग बन रहा है। "

        return {
            "symbol": symbol,
            "current_price": current_price,
            "is_bullish": is_bullish,
            "technical": {
                "trend": tech_trend,
                "rsi": current_rsi,
                "s1": s1, "r1": r1, "s2": s2, "r2": r2
            },
            "astrology": {
                "moon_degree": moon_degree,
                "nakshatra": current_nakshatra,
                "comment": astro_comment
            }
        }
    except Exception as e:
        return {"error": f"Server Error: {str(e)}"}
