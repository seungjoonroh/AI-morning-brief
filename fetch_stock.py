import json
from datetime import datetime
import yfinance as yf

# 관심 종목 설정
SYMBOLS = [
    {"label": "코스피",     "ticker": "^KS11"},
    {"label": "코스닥",     "ticker": "^KQ11"},
    {"label": "삼성전자",   "ticker": "005930.KS"},
    {"label": "S&P 500",   "ticker": "^GSPC"},
    {"label": "나스닥",     "ticker": "^IXIC"},
    {"label": "달러/원",    "ticker": "KRW=X"},
]

def fetch_stock(label, ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="2d")  # 오늘 + 전일 (등락률 계산용)

    if hist.empty or len(hist) < 1:
        return {"label": label, "ticker": ticker, "error": "데이터 없음"}

    latest = hist.iloc[-1]
    price  = round(latest["Close"], 2)

    # 등락률 계산
    if len(hist) >= 2:
        prev_close = hist.iloc[-2]["Close"]
        change     = round(price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2)
    else:
        change     = 0
        change_pct = 0

    sign = "+" if change >= 0 else ""

    return {
        "label":      label,
        "ticker":     ticker,
        "price":      price,
        "change":     change,
        "change_pct": change_pct,
        "display":    f"{sign}{change} ({sign}{change_pct}%)",
        "date":       hist.index[-1].strftime("%Y-%m-%d"),
    }

def fetch_all():
    result = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stocks": []
    }

    print("=" * 40)
    print("  주가 브리핑")
    print(f"  수집: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)

    for s in SYMBOLS:
        data = fetch_stock(s["label"], s["ticker"])
        result["stocks"].append(data)

        if "error" in data:
            print(f"  {data['label']:10} 오류: {data['error']}")
        else:
            print(f"  {data['label']:10} {data['price']:>10,.2f}  {data['display']}")

    print("=" * 40)
    return result

if __name__ == "__main__":
    data = fetch_all()

    with open("stock_result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("stock_result.json 저장 완료")
