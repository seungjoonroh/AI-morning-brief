import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import os

API_KEY = os.environ.get("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

INTEREST_KEYWORDS = [
    "AI",
    "반도체",
    "코스피",
]

def fetch_by_keyword(keyword, page_size=10):
    """키워드로 뉴스 검색 (중복 제거 여유분 확보를 위해 10개 요청)"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = urllib.parse.urlencode({
        "q": keyword,
        "from": yesterday,
        "sortBy": "relevancy",        # publishedAt → relevancy 로 변경
        "language": "ko",
        "pageSize": page_size,
        "apiKey": API_KEY,
    })

    url = f"{BASE_URL}?{params}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    articles = []
    seen_urls = set()
    seen_titles = set()

    for a in data.get("articles", []):
        url_val   = a.get("url", "")
        title_val = a.get("title", "").strip()

        # 1) URL 중복 제거
        if url_val in seen_urls:
            continue
        # 2) 제목 중복 제거 (속보처럼 제목이 동일한 경우)
        if title_val in seen_titles:
            continue
        # 3) 관련도 필터: 제목 또는 설명에 키워드 포함 여부 확인
        description = a.get("description") or ""
        combined = (title_val + " " + description).lower()
        if keyword.lower() not in combined:
            continue

        seen_urls.add(url_val)
        seen_titles.add(title_val)

        articles.append({
            "title":        title_val,
            "source":       a.get("source", {}).get("name", ""),
            "url":          url_val,
            "published_at": a.get("publishedAt", "")[:10],
            "description":  description[:80] + "..." if len(description) > 80 else description,
        })

        if len(articles) == 5:   # 최종 5개만 사용
            break

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

        if not articles:
            print("  관련 기사 없음")
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
