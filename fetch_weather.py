import urllib.request
import urllib.parse
import json
from datetime import datetime

# ──────────────────────────────────────
# 날씨 도시 설정 (3개 도시)
# ──────────────────────────────────────
WEATHER_CITIES = [
    {"city": "서울",   "lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul"},
    {"city": "이타카", "lat": 42.4440, "lon": -76.5019, "tz": "America/New_York"},
    {"city": "파리",   "lat": 48.8566, "lon": 2.3522,   "tz": "Europe/Paris"},
]


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
        f"&forecast_days=2"
    )
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())

    current = data["current"]
    daily   = data["daily"]
    local_time_str = current.get("time", "")

    today_forecast = {
        "temp_max":      daily["temperature_2m_max"][0],
        "temp_min":      daily["temperature_2m_min"][0],
        "precipitation": daily["precipitation_sum"][0],
        "condition":     interpret_weather_code(daily["weather_code"][0]),
    }

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
        "local_time": local_time_str,
        "current": {
            "temperature": current["temperature_2m"],
            "humidity":    current["relative_humidity_2m"],
            "wind_speed":  current["wind_speed_10m"],
            "condition":   interpret_weather_code(current["weather_code"]),
        },
        "today":    today_forecast,
        "tomorrow": tomorrow_forecast,
    }


def fetch_all():
    """모든 도시 날씨 수집"""
    results = []
    for city_config in WEATHER_CITIES:
        try:
            w = fetch_weather_for_city(city_config)
            results.append(w)
        except Exception as e:
            print(f"  {city_config['city']}: 수집 실패 - {e}")
            results.append({"city": city_config["city"], "error": str(e)})
    return results


def print_weather(weather_list):
    """터미널에 날씨 출력"""
    print("=" * 50)
    print("  3도시 날씨 브리핑")
    print(f"  수집: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    for w in weather_list:
        if "error" in w:
            print(f"\n  📍 {w['city']}: 오류 - {w['error']}")
            continue

        c = w["current"]
        t = w["today"]

        # 로컬 시간 파싱 (형식: "2026-03-21T07:30")
        local_display = w["local_time"].replace("T", " ") if w.get("local_time") else "시간 정보 없음"

        print(f"\n  📍 {w['city']} (현지 {local_display})")
        print(f"     현재  {c['temperature']}°C  {c['condition']}")
        print(f"     습도  {c['humidity']}%   바람 {c['wind_speed']} km/h")
        print(f"     오늘  최고 {t['temp_max']}°C / 최저 {t['temp_min']}°C  강수 {t['precipitation']}mm")

        if w.get("tomorrow"):
            tm = w["tomorrow"]
            print(f"     내일  최고 {tm['temp_max']}°C / 최저 {tm['temp_min']}°C  강수 {tm['precipitation']}mm  {tm['condition']}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    weather_list = fetch_all()
    print_weather(weather_list)

    with open("weather_result.json", "w", encoding="utf-8") as f:
        json.dump(weather_list, f, ensure_ascii=False, indent=2)
    print("weather_result.json 저장 완료")
