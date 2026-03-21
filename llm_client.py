import urllib.request
import json
import os

# LLM_PROVIDER: "gemini" 또는 "claude"
PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")

GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-2.0-flash:generateContent"
)
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _call_gemini(prompt):
    url  = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.3},
    }).encode()

    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())

    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_claude(prompt):
    body = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        ANTHROPIC_URL, data=body,
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())

    return data["content"][0]["text"].strip()


def summarize(prompt):
    """프로바이더에 따라 자동으로 LLM 호출"""
    try:
        if PROVIDER == "claude":
            return _call_claude(prompt)
        else:
            return _call_gemini(prompt)
    except Exception as e:
        return f"요약 실패: {e}"


def summarize_news(keyword, articles):
    """키워드별 뉴스 기사 목록을 받아 한국어 요약 반환"""
    if not articles:
        return "관련 기사가 없습니다."

    headlines = "\n".join(
        f"- {a['title']} ({a['source']})"
        for a in articles
    )
    prompt = f"""다음은 '{keyword}' 관련 오늘의 뉴스 헤드라인입니다.

{headlines}

위 뉴스들을 바탕으로 오늘의 '{keyword}' 동향을 2~3문장으로 간결하게 한국어로 요약해주세요.
불필요한 서두 없이 바로 요약 내용만 작성하세요."""

    return summarize(prompt)
