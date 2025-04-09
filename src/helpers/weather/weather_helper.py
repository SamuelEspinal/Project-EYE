import discord
import requests
import os
from dotenv import load_dotenv
import datetime
from collections import defaultdict, Counter

load_dotenv()
OWM_API_KEY = os.getenv('OWM_API_KEY')

#### Helper function to convert country code to emoji flag ####
def country_code_to_emoji(code):
    if not code or len(code) != 2:
        return ""
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

#### Helper function to convert weather description to emoji ####
def weather_to_emoji(description):
    description = description.lower()
    if "clear" in description:
        return "☀️"
    elif "cloud" in description:
        return "☁️"
    elif "rain" in description:
        return "🌧️"
    elif "drizzle" in description:
        return "🌦️"
    elif "thunderstorm" in description:
        return "⛈️"
    elif "snow" in description:
        return "❄️"
    elif "mist" in description or "fog" in description:
        return "🌫️"
    elif "smoke" in description:
        return "💨"
    elif "dust" in description or "sand" in description:
        return "🌪️"
    else:
        return "🌈"

#### Group forecast entries by day ####
def group_forecasts_by_day(forecasts):
    grouped = defaultdict(list)
    for entry in forecasts:
        date = datetime.datetime.fromtimestamp(entry['dt']).date()
        grouped[date].append(entry)
    return grouped

#### Summarize each day's weather ####
"""
    NOTE: If entries contains 8 forecast slices (3-hour intervals for a single day), it might look like:
    [
        {'main': {'temp': 22.5}, 'weather': [{'description': 'clear sky'}]},
        {'main': {'temp': 20.1}, 'weather': [{'description': 'few clouds'}]},
        ...
    ]
    Then summarize_day(entries) might return:
    {
        "desc": "☀️ Clear Sky",
        "high": 24.7,
        "low": 18.2
    }
"""
def summarize_day(entries):
    # Extract all temperature readings for the day into a list
    temps_c = [e['main']['temp'] for e in entries]

    temps_f = [(c * 9/5) + 32 for c in temps_c]
    # Extract all weather descriptions (like 'light rain', 'clear sky') for the day
    descriptions = [e['weather'][0]['description'].title() for e in entries]

    # Find the most frequently occurring weather description
    # e.g., if there are multiple 'Clear Sky' entries, it will be picked
    most_common_desc = Counter(descriptions).most_common(1)[0][0]
    emoji = weather_to_emoji(most_common_desc)

    return {
        "desc": f"{emoji} {most_common_desc}",
        "high": round(max(temps_f), 1),
        "low": round(min(temps_f), 1)
    }

#### Main weather function using free 5-day forecast API ####
async def weather(ctx, location):
    print(f"WEATHER COMMAND - Received location: {location}")
    # Step 1: Get geolocation data
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OWM_API_KEY}"
    geo_response = requests.get(geocode_url).json()

    if not geo_response:
        await ctx.send("\u274c Couldn't find that location. Try including a country code, like `Springfield, US`.")
        return

    country_code = geo_response[0].get('country', '')
    city_name = geo_response[0]['name']
    flag = country_code_to_emoji(country_code)
    resolved_name = f"{flag} {city_name}, {country_code}"

    # Step 2: Fetch 5-day / 3-hour forecast data
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={OWM_API_KEY}"
    forecast_data = requests.get(forecast_url).json()

    if 'list' not in forecast_data:
        await ctx.send("\u274c Could not fetch forecast data. Please try again later.")
        return

    grouped = group_forecasts_by_day(forecast_data['list'])

    # Step 3: Build Discord embed
    embed = discord.Embed(title=f"5-Day Forecast for {resolved_name}", color=discord.Color.blue())
    for date, entries in list(grouped.items())[:5]:
        summary = summarize_day(entries)
        date_str = date.strftime("%A, %b %d")
        embed.add_field(
            name=date_str,
            value=f"{summary['desc']}\n🌡️ High: {summary['high']}°F / Low: {summary['low']}°F",
            inline=False
        )

    await ctx.send(embed=embed)
