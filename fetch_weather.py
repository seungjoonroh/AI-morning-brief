import urllib.request
import json
from datetime import datetime

# 서울 좌표
LATITUDE = 37.5665
LONGITUDE = 126.9780
CITY_NAME = "서울"

def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,weather_code"
        f"&timezone=Asia%2FSeoul"
        f"&forecast_days=1"
    )

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    current = data["current"]
    daily   = data["daily"]

    weather_code = current["weather_code"]
    condition = interpret_weather_code(weather_code)

    result = {
        "city": CITY_NAME,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "current": {
            "temperature":   current["temperature_2m"],
            "humidity":      current["relative_humidity_2m"],
            "wind_speed":    current["wind_speed_10m"],
            "condition":     condition,
        },
        "today": {
            "temp_max":      daily["temperature_2m_max"][0],
            "temp_min":      daily["temperature_2m_min"][0],
            "precipitation": daily["precipitation_sum"][0],
            "condition":     interpret_weather_code(daily["weather_code"][0]),
        }
    }
    return result

def interpret_weather_code(code):
    if code == 0:
        return "맑음"
    elif code in (1, 2, 3):
        return "구름 조금" if code == 1 else ("구름 많음" if code == 2 else "흐림")
    elif code in range(51, 68):
        return "비"
    elif code in range(71, 78):
        return "눈"
    elif code in range(80, 83):
        return "소나기"
    elif code in range(95, 100):
        return "천둥번개"
    else:
        return f"기타({code})"

def print_weather(w):
    c = w["current"]
    t = w["today"]
    print("=" * 40)
    print(f"  {w['city']} 날씨 브리핑")
    print(f"  수집: {w['fetched_at']}")
    print("=" * 40)
    print(f"  현재  {c['temperature']}°C  {c['condition']}")
    print(f"  습도  {c['humidity']}%   바람 {c['wind_speed']} km/h")
    print(f"  오늘  최고 {t['temp_max']}°C / 최저 {t['temp_min']}°C")
    print(f"  강수  {t['precipitation']} mm")
    print("=" * 40)

if __name__ == "__main__":
    weather = fetch_weather()
    print_weather(weather)
    # JSON으로도 저장 (나중에 다른 스크립트가 읽을 수 있도록)
    with open("weather_result.json", "w", encoding="utf-8") as f:
        json.dump(weather, f, ensure_ascii=False, indent=2)
    print("weather_result.json 저장 완료")
