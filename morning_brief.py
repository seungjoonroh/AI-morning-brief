import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import os
import yfinance as yf
from llm_client import summarize_news

# ──────────────────────────────────────
# API 키
# ──────────────────────────────────────
NEWS_API_KEY  = os.environ.get("NEWS_API_KEY")
NEWS_BASE_URL = "https://newsapi.org/v2/everything"

# ──────────────────────────────────────
# 날씨 도시 설정 (3개 도시)
# - city: 표시 이름
# - lat/lon: 위도/경도
# - tz: Open-Meteo 타임존 문자열
# ──────────────────────────────────────
WEATHER_CITIES = [
    {"city": "서울",   "lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul"},
    {"city": "이타카", "lat": 42.4440, "lon": -76.5019, "tz": "America/New_York"},
    {"city": "파리",   "lat": 48.8566, "lon": 2.3522,   "tz": "Europe/Paris"},
]

# ──────────────────────────────────────
# 관심 키워드 (뉴스)
# ──────────────────────────────────────
INTEREST_KEYWORDS = [
    "AI",
    "반도체",
    {"label": "코스피", "query": "코스피 OR 주식시장 OR 증시"},
]

# ──────────────────────────────────────
# 주가/환율 종목
# ──────────────────────────────────────
STOCK_SYMBOLS = [
    {"label": "코스피",   "ticker": "^KS11"},
    {"label": "코스닥",   "ticker": "^KQ11"},
    {"label": "삼성전자", "ticker": "005930.KS"},
    {"label": "S&P 500", "ticker": "^GSPC"},
    {"label": "나스닥",   "ticker": "^IXIC"},
    {"label": "달러/원",  "ticker": "KRW=X"},
]


# ──────────────────────────────────────
# 날씨 관련 함수
# ──────────────────────────────────────
def interpret_weather_code(code):
    """WMO 날씨 코드 → 한글 상태 텍스트"""
    if code == 0:                return "맑음"
    elif code in (1, 2, 3):      return "구름 조금" if code == 1 else ("구름 많음" if code == 2 else "흐림")
    elif code in range(51, 68):  return "비"
    elif code in range(71, 78):  return "눈"
    elif code in range(80, 83):  return "소나기"
    elif code in range(95, 100): return "천둥번개"
    else:                        return f"기타({code})"


def fetch_weather_for_city(city_config):
    """단일 도시의 날씨 데이터를 Open-Meteo API로 수집"""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={city_config['lat']}&longitude={city_config['lon']}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&timezone={urllib.parse.quote(city_config['tz'])}"
        f"&forecast_days=2"  # 오늘 + 내일
    )
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())

    current = data["current"]
    daily   = data["daily"]

    # Open-Meteo가 반환하는 current.time은 해당 도시 로컬 시간
    # 형식: "2026-03-21T07:30" → 파싱해서 표시용으로 사용
    local_time_str = current.get("time", "")

    # 오늘(인덱스 0)과 내일(인덱스 1) 예보
    today_forecast = {
        "temp_max":      daily["temperature_2m_max"][0],
        "temp_min":      daily["temperature_2m_min"][0],
        "precipitation": daily["precipitation_sum"][0],
        "condition":     interpret_weather_code(daily["weather_code"][0]),
    }

    # 내일 데이터가 있으면 포함
    tomorrow_forecast = None
    if len(daily["temperature_2m_max"]) >= 2:
        tomorrow_forecast = {
            "temp_max":      daily["temperature_2m_max"][1],
            "temp_min":      daily["temperature_2m_min"][1],
            "precipitation": daily["precipitation_sum"][1],
            "condition":     interpret_weather_code(daily["weather_code"][1]),
        }

    return {
        "city":       city_config["city"],
        "timezone":   city_config["tz"],
        "local_time": local_time_str,   # "2026-03-21T07:30" 형식
        "current": {
            "temperature": current["temperature_2m"],
            "humidity":    current["relative_humidity_2m"],
            "wind_speed":  current["wind_speed_10m"],
            "condition":   interpret_weather_code(current["weather_code"]),
        },
        "today":    today_forecast,
        "tomorrow": tomorrow_forecast,
    }


def fetch_weather():
    """모든 도시의 날씨를 수집하여 리스트로 반환"""
    results = []
    for city_config in WEATHER_CITIES:
        try:
            w = fetch_weather_for_city(city_config)
            results.append(w)
            print(f"  [날씨] {city_config['city']}: {w['current']['temperature']}°C {w['current']['condition']}")
        except Exception as e:
            print(f"  [날씨] {city_config['city']}: 수집 실패 - {e}")
            # 실패해도 나머지 도시는 계속 수집
            results.append({
                "city":  city_config["city"],
                "error": str(e),
            })
    return results


# ──────────────────────────────────────
# 뉴스 관련 함수
# ──────────────────────────────────────
def fetch_news_by_keyword(keyword_config, page_size=15):
    if isinstance(keyword_config, dict):
        label = keyword_config["label"]
        query = keyword_config["query"]
    else:
        label = keyword_config
        query = keyword_config

    yesterday = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
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
            if not any(w.lower() in combined for w in query.split(" OR ")):
                continue
        if source_count.get(source, 0) >= 2:
            continue

        seen_urls.add(url_val)
        seen_titles.add(title_val)
        source_count[source] = source_count.get(source, 0) + 1
        articles.append({
            "title":        title_val,
            "source":       source,
            "url":          url_val,
            "published_at": a.get("publishedAt", "")[:10],
        })
        if len(articles) == 5:
            break

    return label, articles


def fetch_news():
    result = {}
    for kw in INTEREST_KEYWORDS:
        label, articles = fetch_news_by_keyword(kw)
        print(f"  [뉴스] {label}: {len(articles)}건 수집 → 요약 중...")
        summary = summarize_news(label, articles)
        result[label] = {"articles": articles, "summary": summary}
        print(f"    요약: {summary[:60]}...")
    return result


# ──────────────────────────────────────
# 주가 관련 함수
# ──────────────────────────────────────
def fetch_stock(label, ticker):
    hist = yf.Ticker(ticker).history(period="2d")
    if hist.empty:
        return {"label": label, "ticker": ticker, "error": "데이터 없음"}
    price = round(hist.iloc[-1]["Close"], 2)
    if len(hist) >= 2:
        prev       = hist.iloc[-2]["Close"]
        change     = round(price - prev, 2)
        change_pct = round((change / prev) * 100, 2)
    else:
        change = change_pct = 0
    sign = "+" if change >= 0 else ""
    return {
        "label":      label,
        "ticker":     ticker,
        "price":      price,
        "change":     change,
        "change_pct": change_pct,
        "display":    f"{sign}{change} ({sign}{change_pct}%)",
    }


def fetch_stocks():
    return [fetch_stock(s["label"], s["ticker"]) for s in STOCK_SYMBOLS]


# ──────────────────────────────────────
# 메인 실행
# ──────────────────────────────────────
if __name__ == "__main__":
    if not NEWS_API_KEY:
        print("오류: NEWS_API_KEY 없음")
        exit(1)

    print("데이터 수집 중...")
    brief = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weather":  fetch_weather(),    # 변경: 단일 객체 → 리스트
        "stocks":   fetch_stocks(),
        "news":     fetch_news(),
    }

    with open("brief_result.json", "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)

    print("brief_result.json 저장 완료")
