import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import os

API_KEY = os.environ.get("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

# 키워드: 문자열 또는 {"label": ..., "query": ...} 형태 모두 지원
INTEREST_KEYWORDS = [
    "AI",
    "반도체",
    {"label": "코스피", "query": "코스피 OR 주식시장 OR 증시"},
]

def fetch_by_keyword(keyword_config, page_size=15):
    """키워드로 뉴스 검색 (소스 편중 방지 + 중복 제거)"""

    if isinstance(keyword_config, dict):
        label = keyword_config["label"]
        query = keyword_config["query"]
    else:
        label = keyword_config
        query = keyword_config

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = urllib.parse.urlencode({
        "q":        query,
        "from":     yesterday,
        "sortBy":   "relevancy",
        "language": "ko",
        "pageSize": page_size,
        "apiKey":   API_KEY,
    })

    url = f"{BASE_URL}?{params}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    articles = []
    seen_urls    = set()
    seen_titles  = set()
    source_count = {}

    for a in data.get("articles", []):
        url_val   = a.get("url", "")
        title_val = a.get("title", "").strip()
        source    = a.get("source", {}).get("name", "")

        # 중복 제거
        if url_val in seen_urls or title_val in seen_titles:
            continue

        # 관련도 필터
        description = a.get("description") or ""
        combined    = (title_val + " " + description).lower()
        check_word  = label.lower()
        if check_word not in combined:
            query_words = [w.lower() for w in query.split(" OR ")]
            if not any(w in combined for w in query_words):
                continue

        # 소스 편중 방지: 동일 출처 최대 2개
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
            "description":  description[:80] + "..." if len(description) > 80 else description,
        })

        if len(articles) == 5:
            break

    return label, articles

def fetch_all():
    result = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "keywords": {}
    }

    for keyword_config in INTEREST_KEYWORDS:
        label, articles = fetch_by_keyword(keyword_config)
        result["keywords"][label] = articles

        print(f"\n[{label}] 검색 중...")
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
