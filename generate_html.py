import json
from datetime import datetime

def load_brief(path=“brief_result.json”):
with open(path, encoding=“utf-8”) as f:
return json.load(f)

def stock_color(change):
if change > 0:  return “#e53e3e”
if change < 0:  return “#3182ce”
return “#718096”

def stock_arrow(change):
if change > 0:  return “▲”
if change < 0:  return “▼”
return “—”

def weather_emoji(condition):
table = {
“맑음”: “☀️”, “구름 조금”: “🌤️”, “구름 많음”: “⛅”,
“흐림”: “☁️”, “비”: “🌧️”, “눈”: “❄️”,
“소나기”: “🌦️”, “천둥번개”: “⛈️”,
}
return table.get(condition, “🌡️”)

def format_local_time(time_str):
“””‘2026-03-21T07:30’ → ‘3/21 07:30’ 형식으로 변환”””
if not time_str:
return “”
try:
dt = datetime.strptime(time_str, “%Y-%m-%dT%H:%M”)
return f”{dt.month}/{dt.day} {dt.strftime(’%H:%M’)}”
except ValueError:
return time_str

def generate_weather_card(w, idx):
“”“단일 도시의 날씨 카드 HTML 생성 (idx: 도시 인덱스, 실시간 업데이트용 id)”””
if “error” in w:
return f”””
<div class="weather-city" id="weather-city-{idx}">
<div class="weather-city-name">{w[‘city’]}</div>
<div style="color:#718096">날씨 데이터를 불러올 수 없습니다</div>
</div>”””

```
c  = w["current"]
t  = w["today"]
we = weather_emoji(c["condition"])
local_time = format_local_time(w.get("local_time", ""))

# 내일 예보 (있으면 표시)
tomorrow_html = ""
if w.get("tomorrow"):
    tm = w["tomorrow"]
    tm_emoji = weather_emoji(tm["condition"])
    tomorrow_html = f"""
    <div class="weather-forecast">
      <span class="forecast-label">내일</span>
      {tm_emoji} {tm['condition']} · {tm['temp_min']}°~{tm['temp_max']}°C · 강수 {tm['precipitation']}mm
    </div>"""

return f"""
<div class="weather-city" id="weather-city-{idx}">
  <div class="weather-city-header">
    <div class="weather-city-name">{w['city']}</div>
    <div class="weather-local-time" id="local-time-{idx}">{local_time}</div>
  </div>
  <div class="weather-main">
    <div class="weather-emoji" id="weather-emoji-{idx}">{we}</div>
    <div>
      <div class="weather-temp" id="weather-temp-{idx}">{c['temperature']}°C</div>
      <div class="weather-condition" id="weather-cond-{idx}">{c['condition']}</div>
    </div>
  </div>
  <div class="weather-detail">
    <span>💧 습도 <span id="humidity-{idx}">{c['humidity']}</span>%</span>
    <span>💨 바람 <span id="wind-{idx}">{c['wind_speed']}</span> km/h</span>
    <span>🌡 {t['temp_min']}°~{t['temp_max']}°C</span>
    <span>☔ 강수 {t['precipitation']}mm</span>
  </div>
  {tomorrow_html}
</div>"""
```

def generate_html(brief):
generated = brief.get(“generated_at”, “”)

```
# ── 날씨: 리스트(3도시) 또는 기존 단일 객체 호환 ──
weather_data = brief["weather"]
if isinstance(weather_data, list):
    weather_cards = "\n".join(
        generate_weather_card(w, i) for i, w in enumerate(weather_data)
    )
else:
    weather_cards = generate_weather_card(weather_data, 0)

# ── 주가 테이블 ──
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

# ── 뉴스 섹션 ──
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

# ── 전체 HTML ──
html = f"""<!DOCTYPE html>
```

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

```
/* 헤더 */
.header {{
  background: linear-gradient(135deg, #1a202c, #2d3748);
  color: white;
  border-radius: 16px;
  padding: 28px 24px;
  margin-bottom: 20px;
}}
.header h1 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }}
.header .subtitle {{ font-size: 0.85rem; color: #a0aec0; }}
.live-badge {{
  display: inline-block;
  font-size: 0.7rem;
  background: #48bb78;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: 8px;
  vertical-align: middle;
  animation: pulse 2s infinite;
}}
@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.6; }}
}}

/* 카드 공통 */
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

/* 날씨 — 3도시 그리드 */
.weather-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}}
@media (min-width: 600px) {{
  .weather-grid {{
    grid-template-columns: repeat(3, 1fr);
  }}
}}
.weather-city {{
  background: #f7f8fa;
  border-radius: 12px;
  padding: 14px 16px;
}}
.weather-city-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}}
.weather-city-name {{
  font-size: 0.95rem;
  font-weight: 700;
  color: #2d3748;
}}
.weather-local-time {{
  font-size: 0.75rem;
  color: #718096;
  background: #edf2f7;
  padding: 2px 8px;
  border-radius: 8px;
}}
.weather-main {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}}
.weather-emoji {{ font-size: 2.2rem; }}
.weather-temp {{ font-size: 1.8rem; font-weight: 700; }}
.weather-condition {{ font-size: 0.85rem; color: #4a5568; }}
.weather-detail {{
  display: flex;
  gap: 10px;
  font-size: 0.75rem;
  color: #718096;
  flex-wrap: wrap;
}}
.weather-forecast {{
  margin-top: 8px;
  font-size: 0.78rem;
  color: #4a5568;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}}
.forecast-label {{
  font-weight: 600;
  color: #718096;
  margin-right: 4px;
}}

/* 주가 */
table {{ width: 100%; border-collapse: collapse; }}
td {{ padding: 8px 4px; font-size: 0.9rem; }}
tr:not(:last-child) td {{ border-bottom: 1px solid #f0f0f0; }}
.stock-label {{ color: #2d3748; font-weight: 500; width: 30%; }}
.stock-price {{ text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }}
.stock-change {{ text-align: right; font-variant-numeric: tabular-nums; font-size: 0.85rem; }}

/* 뉴스 */
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
```

  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📰 AI 모닝 브리핑</h1>
      <div class="subtitle">
        뉴스·주가 {generated} 기준 ·
        날씨 <span id="weather-update-time">업데이트 중...</span>
        <span class="live-badge" id="live-badge" style="display:none">LIVE</span>
      </div>
    </div>

```
<div class="card">
  <h2>🌤 날씨</h2>
  <div class="weather-grid">
    {weather_cards}
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

<div class="footer">AI Morning Brief · 매일 오전 7시 자동 업데이트 · 날씨는 실시간</div>
```

  </div>

  <script>
  // ──────────────────────────────────────
  // 실시간 날씨 업데이트
  // 페이지를 열 때 Open-Meteo API를 브라우저에서 직접 호출
  // 현재 기온, 날씨 상태, 습도, 바람, 현지 시간을 갱신
  // 실패 시 아침 7시에 생성된 정적 데이터가 그대로 유지됨
  // ──────────────────────────────────────

  const CITIES = [
    {{ city: "서울",   lat: 37.5665, lon: 126.9780, tz: "Asia/Seoul" }},
    {{ city: "이타카", lat: 42.4440, lon: -76.5019, tz: "America/New_York" }},
    {{ city: "파리",   lat: 48.8566, lon: 2.3522,   tz: "Europe/Paris" }},
  ];

  // WMO 날씨 코드 → [한글 상태, 이모지]
  function weatherInfo(code) {{
    const map = {{
      0: ["맑음", "☀️"],
      1: ["구름 조금", "🌤️"], 2: ["구름 많음", "⛅"], 3: ["흐림", "☁️"],
      51: ["비", "🌧️"], 53: ["비", "🌧️"], 55: ["비", "🌧️"],
      61: ["비", "🌧️"], 63: ["비", "🌧️"], 65: ["비", "🌧️"],
      71: ["눈", "❄️"], 73: ["눈", "❄️"], 75: ["눈", "❄️"],
      80: ["소나기", "🌦️"], 81: ["소나기", "🌦️"], 82: ["소나기", "🌦️"],
      95: ["천둥번개", "⛈️"], 96: ["천둥번개", "⛈️"], 99: ["천둥번개", "⛈️"],
    }};
    return map[code] || ["기타", "🌡️"];
  }}

  // 특정 타임존의 현재 시각을 "M/D HH:MM" 형식으로 반환
  function getLocalTime(tz) {{
    const now = new Date();
    const opts = {{ timeZone: tz, hour: "2-digit", minute: "2-digit", hour12: false }};
    const dateOpts = {{ timeZone: tz, month: "numeric", day: "numeric" }};
    const time = now.toLocaleTimeString("en-GB", opts);
    const date = now.toLocaleDateString("en-US", dateOpts);
    return date + " " + time;
  }}

  // Open-Meteo API 호출 → 각 도시 날씨 DOM 업데이트
  async function updateWeatherLive() {{
    for (let i = 0; i < CITIES.length; i++) {{
      const c = CITIES[i];
      try {{
        const url =
          "https://api.open-meteo.com/v1/forecast" +
          "?latitude=" + c.lat +
          "&longitude=" + c.lon +
          "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m" +
          "&timezone=" + encodeURIComponent(c.tz);

        const resp = await fetch(url);
        const data = await resp.json();
        const cur = data.current;

        const [condText, condEmoji] = weatherInfo(cur.weather_code);

        // 각 요소를 id로 찾아서 업데이트
        const tempEl  = document.getElementById("weather-temp-" + i);
        const condEl  = document.getElementById("weather-cond-" + i);
        const emojiEl = document.getElementById("weather-emoji-" + i);
        const timeEl  = document.getElementById("local-time-" + i);
        const humidEl = document.getElementById("humidity-" + i);
        const windEl  = document.getElementById("wind-" + i);

        if (tempEl)  tempEl.textContent  = cur.temperature_2m + "°C";
        if (condEl)  condEl.textContent  = condText;
        if (emojiEl) emojiEl.textContent = condEmoji;
        if (timeEl)  timeEl.textContent  = getLocalTime(c.tz);
        if (humidEl) humidEl.textContent = cur.relative_humidity_2m;
        if (windEl)  windEl.textContent  = cur.wind_speed_10m;

      }} catch (e) {{
        console.warn(c.city + " 실시간 날씨 업데이트 실패:", e);
        // 실패 시 기존 정적 데이터 유지
      }}
    }}

    // 현지 시간도 갱신
    updateLocalTimes();

    // 헤더에 마지막 업데이트 시각 표시 + LIVE 배지
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const updateEl = document.getElementById("weather-update-time");
    const badgeEl  = document.getElementById("live-badge");
    if (updateEl) updateEl.textContent = hh + ":" + mm + " 실시간";
    if (badgeEl)  badgeEl.style.display = "inline-block";
  }}

  // 현지 시간만 매분 갱신 (API 호출 없이)
  function updateLocalTimes() {{
    for (let i = 0; i < CITIES.length; i++) {{
      const timeEl = document.getElementById("local-time-" + i);
      if (timeEl) {{
        timeEl.textContent = getLocalTime(CITIES[i].tz);
      }}
    }}
  }}

  // ── 실행 ──
  // 페이지 로드 시 즉시 실시간 데이터 가져오기
  updateWeatherLive();

  // 현지 시간: 1분마다 갱신
  setInterval(updateLocalTimes, 60000);

  // 날씨 데이터: 10분마다 갱신
  setInterval(updateWeatherLive, 600000);
  </script>

</body>
</html>"""

```
return html
```

if **name** == “**main**”:
brief = load_brief()
html  = generate_html(brief)
with open(“docs/index.html”, “w”, encoding=“utf-8”) as f:
f.write(html)
print(“docs/index.html 생성 완료”)