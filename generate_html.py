import json
from datetime import datetime

def load_brief(path="brief_result.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def stock_color(change):
    if change > 0:  return "#e53e3e"
    if change < 0:  return "#3182ce"
    return "#718096"

def stock_arrow(change):
    if change > 0:  return "▲"
    if change < 0:  return "▼"
    return "—"

def weather_emoji(condition):
    table = {
        "맑음": "☀️", "구름 조금": "🌤️", "구름 많음": "⛅",
        "흐림": "☁️", "비": "🌧️", "눈": "❄️",
        "소나기": "🌦️", "천둥번개": "⛈️",
    }
    return table.get(condition, "🌡️")

def generate_html(brief):
    generated = brief.get("generated_at", "")
    w  = brief["weather"]
    c  = w["current"]
    t  = w["today"]
    we = weather_emoji(c["condition"])

    stock_rows = ""
    for s in brief["stocks"]:
        if "error" in s:
            stock_rows += f"""
            <tr>
              <td>{s['label']}</td>
              <td colspan="3" style="color:#718096">데이터 없음</td>
            </tr>"""
        else:
            color = stock_color(s["change"])
            arrow = stock_arrow(s["change"])
            sign  = "+" if s["change"] >= 0 else ""
            stock_rows += f"""
            <tr>
              <td class="stock-label">{s['label']}</td>
              <td class="stock-price">{s['price']:,.2f}</td>
              <td style="color:{color}" class="stock-change">{arrow} {sign}{s['change']}</td>
              <td style="color:{color}" class="stock-change">({sign}{s['change_pct']}%)</td>
            </tr>"""

    news_sections = ""
    for label, content in brief["news"].items():
        articles = content.get("articles", [])
        summary  = content.get("summary", "")

        items = ""
        for a in articles:
            items += f"""
            <li>
              <a href="{a['url']}" target="_blank">{a['title']}</a>
              <span class="news-meta">{a['source']} · {a['published_at']}</span>
            </li>"""
        if not articles:
            items = "<li style='color:#718096'>관련 기사 없음</li>"

        news_sections += f"""
        <div class="news-block">
          <h3># {label}</h3>
          <div class="summary">{summary}</div>
          <ul>{items}</ul>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 모닝 브리핑</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f8fa;
      color: #1a202c;
      padding: 24px 16px;
    }}
    .container {{ max-width: 720px; margin: 0 auto; }}
    .header {{
      background: linear-gradient(135deg, #1a202c, #2d3748);
      color: white;
      border-radius: 16px;
      padding: 28px 24px;
      margin-bottom: 20px;
    }}
    .header h1 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }}
    .header .subtitle {{ font-size: 0.85rem; color: #a0aec0; }}
    .card {{
      background: white;
      border-radius: 16px;
      padding: 20px 24px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }}
    .card h2 {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #718096;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 14px;
    }}
    .weather-main {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 12px;
    }}
    .weather-emoji {{ font-size: 3rem; }}
    .weather-temp {{ font-size: 2.5rem; font-weight: 700; }}
    .weather-condition {{ font-size: 1rem; color: #4a5568; margin-top: 2px; }}
    .weather-detail {{
      display: flex;
      gap: 20px;
      font-size: 0.85rem;
      color: #718096;
      flex-wrap: wrap;
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    td {{ padding: 8px 4px; font-size: 0.9rem; }}
    tr:not(:last-child) td {{ border-bottom: 1px solid #f0f0f0; }}
    .stock-label {{ color: #2d3748; font-weight: 500; width: 30%; }}
    .stock-price {{ text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }}
    .stock-change {{ text-align: right; font-variant-numeric: tabular-nums; font-size: 0.85rem; }}
    .news-block {{ margin-bottom: 24px; }}
    .news-block:last-child {{ margin-bottom: 0; }}
    .news-block h3 {{
      font-size: 0.85rem;
      font-weight: 700;
      color: #4a5568;
      margin-bottom: 8px;
    }}
    .summary {{
      background: #f0f4ff;
      border-left: 3px solid #4a6fa5;
      border-radius: 0 8px 8px 0;
      padding: 10px 14px;
      font-size: 0.88rem;
      color: #2d3748;
      line-height: 1.6;
      margin-bottom: 12px;
    }}
    .news-block ul {{ list-style: none; }}
    .news-block li {{
      padding: 8px 0;
      border-bottom: 1px solid #f7f8fa;
    }}
    .news-block li:last-child {{ border-bottom: none; }}
    .news-block a {{
      display: block;
      font-size: 0.9rem;
      color: #1a202c;
      text-decoration: none;
      line-height: 1.4;
      margin-bottom: 2px;
    }}
    .news-block a:hover {{ color: #3182ce; }}
    .news-meta {{ font-size: 0.75rem; color: #a0aec0; }}
    .footer {{
      text-align: center;
      font-size: 0.75rem;
      color: #a0aec0;
      margin-top: 8px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📰 AI 모닝 브리핑</h1>
      <div class="subtitle">{generated} 기준</div>
    </div>

    <div class="card">
      <h2>🌤 날씨 — {w['city']}</h2>
      <div class="weather-main">
        <div class="weather-emoji">{we}</div>
        <div>
          <div class="weather-temp">{c['temperature']}°C</div>
          <div class="weather-condition">{c['condition']}</div>
        </div>
      </div>
      <div class="weather-detail">
        <span>💧 습도 {c['humidity']}%</span>
        <span>💨 바람 {c['wind_speed']} km/h</span>
        <span>🌡 최고 {t['temp_max']}°C / 최저 {t['temp_min']}°C</span>
        <span>☔ 강수 {t['precipitation']} mm</span>
      </div>
    </div>

    <div class="card">
      <h2>📈 주가</h2>
      <table>{stock_rows}</table>
    </div>

    <div class="card">
      <h2>📋 뉴스 클리핑</h2>
      {news_sections}
    </div>

    <div class="footer">AI Morning Brief · 매일 오전 7시 자동 업데이트</div>
  </div>
</body>
</html>"""

    return html

if __name__ == "__main__":
    brief = load_brief()
    html  = generate_html(brief)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("docs/index.html 생성 완료")
