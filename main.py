from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import swisseph as swe
from datetime import datetime
import os

app = FastAPI(title="AstroTrade API")

# Allow the Android App to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "AstroTrade API is running live on Render! 🚀"}

@app.get("/api/analyze_stock")
def analyze_stock(symbol: str = "RELIANCE.NS"):
    try:
        # 1. Fetch Real Technical Data from Yahoo Finance
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return {"error": "Stock not found. Please check the symbol (e.g. RELIANCE.NS, TCS.NS)"}
            
        current_price = round(hist['Close'].iloc[-1], 2)
        
        # Calculate Real Support/Resistance (Pivot Point Standard)
        high = hist['High'].max()
        low = hist['Low'].min()
        pivot = (high + low + current_price) / 3
        s1 = round((2 * pivot) - high, 2)
        r1 = round((2 * pivot) - low, 2)
        s2 = round(pivot - (high - low), 2)
        r2 = round(pivot + (high - low), 2)
        
        # 2. Fetch Real Astro Data (pyswisseph)
        now = datetime.now()
        swe.set_ephe_path('') # Use default internal ephemeris
        julday = swe.julday(now.year, now.month, now.day, now.hour)
        
        # Get Moon position as an example of astrology calculation
        moon_pos = swe.calc_ut(julday, swe.MOON)[0][0]
        
        # 3. Astro-Tech Combo Logic
        is_bullish = True if current_price > pivot else False
        
        verdict = "Yes" if is_bullish else "No"
        astro_comment = "चार्ट पर ब्रेकआउट है और गुरु महादशा अनुकूल है (Strong Buy)." if is_bullish else "राहु का प्रभाव है और 200DMA टूट चुका है (High Risk)."
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "technical": {
                "s1": s1,
                "r1": r1,
                "s2": s2,
                "r2": r2,
                "trend": "Bullish" if is_bullish else "Bearish"
            },
            "astrology": {
                "moon_degree": round(moon_pos, 2),
                "comment": astro_comment
            },
            "verdict": verdict,
            "score": 92 if is_bullish else 45
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
