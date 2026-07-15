import json
import webbrowser
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

CITIES = [
    {"name": "Hamburg", "country": "Germany"},
    {"name": "Kyiv", "country": "Ukraine"},
    {"name": "Los Angeles", "country": "USA"},
    {"name": "Semirom", "country": "Iran"},
]

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def get_weather(city: dict) -> dict:
    geocode_url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        f"name={quote(city['name'])}&count=1&language=en&format=json"
    )
    geocode_data = fetch_json(geocode_url)
    location = geocode_data["results"][0]

    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={location['latitude']}&longitude={location['longitude']}&"
        "current=temperature_2m,weather_code,wind_speed_10m&timezone=auto"
    )
    weather_data = fetch_json(weather_url)
    current = weather_data["current"]

    return {
        "city": city["name"],
        "country": city["country"],
        "temperature": round(current["temperature_2m"], 1),
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
        "wind": round(current["wind_speed_10m"], 1),
    }


def build_html(weather_items: list[dict]) -> str:
    cards = []
    for item in weather_items:
        cards.append(
            f"""
            <section class=\"card\">
                <h2>{item['city']}, {item['country']}</h2>
                <p class=\"temp\">{item['temperature']}°C</p>
                <p>{item['condition']}</p>
                <p>Wind: {item['wind']} km/h</p>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Weather Dashboard</title>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #dbeafe, #f8fafc);
            color: #111827;
        }}
        h1 {{
            text-align: center;
            margin: 24px 0 8px;
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1100px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .temp {{
            font-size: 2rem;
            font-weight: bold;
            margin: 8px 0;
        }}
        @media (max-width: 700px) {{
            .container {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <h1>Weather Overview</h1>
    <div class=\"container\">
        {''.join(cards)}
    </div>
</body>
</html>
"""


def main() -> None:
    weather_items = [get_weather(city) for city in CITIES]
    output_path = Path(__file__).with_name("weather_dashboard.html")
    output_path.write_text(build_html(weather_items), encoding="utf-8")
    webbrowser.open(output_path.resolve().as_uri())
    print(f"Opened {output_path}")


if __name__ == "__main__":
    main()
