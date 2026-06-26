"""A command-line weather tool.

Looks up the current weather for a city using the free Open-Meteo API,
which needs no API key. It first geocodes the city name into coordinates,
then fetches the current weather for those coordinates.

Usage:
    python3 weather_cli.py            # then type a city when asked
    python3 weather_cli.py London     # pass the city on the command line
"""

import sys

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10  # seconds

# Open-Meteo returns a numeric weather code; this maps common ones to text.
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
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def describe_code(code):
    return WEATHER_CODES.get(code, "Unknown conditions")


def geocode_city(city):
    """Return (name, country, lat, lon) for a city, or None if not found."""
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    response = requests.get(GEOCODE_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        return None

    top = results[0]
    return (
        top.get("name", city),
        top.get("country", ""),
        top["latitude"],
        top["longitude"],
    )


def fetch_weather(lat, lon):
    """Return the current_weather dict for given coordinates."""
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return data.get("current_weather")


def report_weather(city):
    """Look up and print the weather for a city. Returns True on success."""
    try:
        location = geocode_city(city)
    except requests.exceptions.Timeout:
        print("The geocoding request timed out. Please try again.")
        return False
    except requests.exceptions.RequestException as error:
        print(f"Network error while looking up the city: {error}")
        return False

    if location is None:
        print(f'Could not find a city called "{city}".')
        return False

    name, country, lat, lon = location

    try:
        weather = fetch_weather(lat, lon)
    except requests.exceptions.Timeout:
        print("The weather request timed out. Please try again.")
        return False
    except requests.exceptions.RequestException as error:
        print(f"Network error while fetching the weather: {error}")
        return False

    if not weather:
        print("The weather service did not return any data.")
        return False

    place = f"{name}, {country}".strip(", ")
    print(f"\nCurrent weather in {place}:")
    print(f"  Temperature: {weather.get('temperature')} C")
    print(f"  Wind speed:  {weather.get('windspeed')} km/h")
    print(f"  Conditions:  {describe_code(weather.get('weathercode'))}")
    return True


def main():
    # Take the city from the command line if given, otherwise ask.
    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:])
    else:
        city = input("Enter a city name: ").strip()

    if not city:
        print("No city entered.")
        return

    report_weather(city)


if __name__ == "__main__":
    main()
