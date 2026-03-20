import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import os
import yfinance as yf

# ============================================================
# 설정
# ============================================================
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_BASE_URL = "https://newsapi.org/v2/everything"

WEATHER_LATITUDE  = 37.5665
WEATHER_LONGITUDE = 126.9780
WEATHER_CITY      = "서울"

INTEREST_KEYWORDS = [
    "AI",
    "반도체",
    {"label": "코스피", "query": "코스피 OR 주식시장 OR 증시"},
]

STOCK_SYMBOLS = [
    {"label": "코스피",   "ticker": "^KS11"},
    {"label": "코스닥",   "ticker": "^KQ11"},
    {"label": "삼성전자", "ticker": "005930.KS"},
    {"label": "S&P 500", "ticker": "^GSPC"},
    {"label": "나스닥",   "ticker": "^IXIC"},
    {"label": "달러/원",  "ticker": "KRW=X"},
]

# ============================================================
# 날씨
# ============================================================
def interpret_weather_code(code):
    if code == 0:                  return "맑음"
    elif code in (1, 2, 3):        return "구름 조금" if code == 1 else ("구름 많음" if code == 2 else "흐림")
    elif code in range(51, 68):    return "비"
    elif code in range(71, 78):    return "눈"
    elif code in range(80, 83):    return "소나기"
    elif code in range(95, 100):   return "천둥번개"
    else:                          return f"기타({code})"

def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={WEATHER_LATITUDE}&longitude={WEATHER_LONGITUDE}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&timezone=Asia%2FSeoul&forecast_days=1"
    )
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())

    current = data["current"]
    daily   = data["daily"]
    return {
        "city": WEATHER_CITY,
        "current": {
            "temperature": current["temperature_2m"],
            "humidity":    current["relative_humidity_2m"],
            "wind_speed":  current["wind_speed_10m"],
            "condition":   interpret_weather_code(current["weather_code"]),
        },
        "today": {
            "temp_max":      daily["temperature_2m_max"][0],
            "temp_min":      daily["temperature_2m_min"][0],
            "precipitation": daily["precipitation_sum"][0],
            "condition":     interpret_weather_code(daily["weather_code"][0]),
        }
    }

# ============================================================
# 뉴스
# ============================================================
def fetch_news_by_keyword(keyword_config, page_size=15):
    if isinstance(keyword_config, dict):
        label = keyword_config["label"]
        query = keyword_config["query"]
    else:
        label = keyword_config
        query = keyword_config

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    params = urllib.parse.urlencode({
        "q": query, "from": yesterday,
        "sortBy": "relevancy", "language": "ko",
        "pageSize": page_size, "apiKey": NEWS_API_KEY,
    })
    with urllib.request.urlopen(f"{NEWS_BASE_URL}?{params}") as r:
        data = json.loads(r.read().decode())

    articles = []
    seen_urls, seen_titles, source_count = set(), set(), {}

    for a in data.get("articles", []):
        url_val   = a.get("url", "")
        title_val = a.get("title", "").strip()
        source    = a.get("source", {}).get("name", "")
        desc      = a.get("description") or ""
        combined  = (title_val + " " + desc).lower()

        if url_val in seen_urls or title_val in seen_titles:
            continue
        if label.lower() not in combined:
            if​​​​​​​​​​​​​​​​
