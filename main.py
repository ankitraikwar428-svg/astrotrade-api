from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import swisseph as swe
from datetime import datetime
import urllib.request
import re

app = FastAPI(title="AstroTrade API - Ultimate Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_live_price(symbol):
    try:
        # Google Finance से डायरेक्ट लाइव प्राइस निकालना (No Blocks!)
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        url = f"https://www.google.com/finance/quote/{clean_symbol}:NSE"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'class="YMlKec fxKbKc"[^>]*>₹?([0-9,.]+)<', html)
        if match:
            return float(match.group(1).replace(',', ''))
    except:
        pass
    return None

@app.get("/api/analyze_stock")
def analyze_stock(symbol: str = "RELIANCE.NS"):
    try:
        # 1. LIVE PRICE (Google Finance)
        current_price = get_live_price(symbol)
        
        if current_price is None:
            return {"error": f"स्टॉक '{symbol}' का लाइव डेटा नहीं मिला। कृपया नाम सही डालें (जैसे ZOMATO)।"}
            
        # Support/Resistance based on volatility
        s1 = round(current_price * 0.985, 2)
        r1 = round(current_price * 1.015, 2)
        s2 = round(current_price * 0.97, 2)
        r2 = round(current_price * 1.03, 2)

        # 2. ADVANCED ASTROLOGY MODEL (High Accuracy)
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

        rahu_pos, _ = swe.calc_ut(julday, swe.MEAN_NODE)
        rahu_degree = round(rahu_pos[0], 2)

        is_bullish = True
        tech_trend = "Google Live Connection Active."
        
        astro_comment = f"चंद्रमा '{current_nakshatra}' नक्षत्र में है। "
        good_nakshatras = ["पुष्य", "अनुराधा", "स्वाति", "रोहिणी", "हस्त", "श्रवण", "उत्तरा फाल्गुनी", "उत्तराषाढ़ा", "उत्तरा भाद्रपद"]
        bad_nakshatras = ["भरणी", "कृत्तिका", "आर्द्रा", "आश्लेषा", "ज्येष्ठा", "मूल"]

        if current_nakshatra in good_nakshatras:
            astro_comment += "यह शुभ नक्षत्र शेयर बाज़ार में 'तेज़ी' (Bullish) का संकेत देता है! "
            is_bullish = True
        elif current_nakshatra in bad_nakshatras:
            astro_comment += "अशुभ नक्षत्र के कारण बाज़ार में 'गिरावट' (Bearish) आ सकती है। "
            is_bullish = False
        else:
            astro_comment += "यह नक्षत्र ट्रेडिंग के लिए 'न्यूट्रल' (Neutral) है। "

        # Jupiter & Rahu Logic
        angle_diff = abs(moon_degree - jupiter_degree)
        if 110 < angle_diff < 130 or angle_diff < 10:
            astro_comment += "चार्ट में गुरु का शक्तिशाली 'गजकेसरी योग' बन रहा है (Strong Buy)। "
            is_bullish = True
            
        rahu_diff = abs(moon_degree - rahu_degree)
        if rahu_diff < 15 or abs(rahu_diff - 180) < 15:
            astro_comment += "राहु का साया भी है, इसलिए संभलकर ट्रेड करें (रिस्क ज्यादा है)। "
            is_bullish = False

        return {
            "symbol": symbol,
            "current_price": current_price,
            "is_bullish": is_bullish,
            "technical": {
                "trend": tech_trend,
                "rsi": "N/A",
                "s1": s1, "r1": r1, "s2": s2, "r2": r2
            },
            "astrology": {
                "moon_degree": moon_degree,
                "nakshatra": current_nakshatra,
                "comment": astro_comment
            }
        }
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
