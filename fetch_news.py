import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import os

API_KEY = os.environ.get("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

# 관심 키워드 목록 (나중에 별도 설정 파일로 분리 예정)
INTEREST_KEYWORDS = [
    "AI",
    "반도체",
    "코스피",
]

def fetch_by_keyword(keyword, page_size=5):
    """키워드로 뉴스 검색"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = urllib.parse.urlencode({
        "q": keyword,
        "from": yesterday,
        "sortBy": "publishedAt",
        "language": "ko",
        "pageSize": page_size,
        "apiKey": API_KEY,
    })

    url = f"{BASE_URL}?{params}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    articles = []
    for a in data.get("articles", []):
        articles.append({
            "title":  a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url":    a.get("url", ""),
            "published_at": a.get("publishedAt", "")[:10],
        })
    return articles

def fetch_all():
    result = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "keywords": {}
    }

    for keyword in INTEREST_KEYWORDS:
        print(f"\n[{keyword}] 검색 중...")
        articles = fetch_by_keyword(keyword)
        result["keywords"][keyword] = articles

        for i, a in enumerate(articles, 1):
            print(f"  {i}. {a['title']}")
            print(f"     출처: {a['source']} | {a['published_at']}")

    return result

if __name__ == "__main__":
    if not API_KEY:
        print("오류: NEWS_API_KEY 환경변수가 없습니다.")
        exit(1)

    print("=" * 40)
    print("  뉴스 클리핑 브리핑")
    print(f"  수집: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)

    data = fetch_all()

    with open("news_result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nnews_result.json 저장 완료")
