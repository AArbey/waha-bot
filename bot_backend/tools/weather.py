import requests
from pydantic import BaseModel, Field, ValidationError

class WeatherArgs(BaseModel):
    city: str = Field(min_length=1, description="Name of the city, ex : Paris")

def getWeather(city: str) -> str:
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "fr"},
            timeout=10,
        ).json()
    except requests.HTTPError:
        return "Service de géolocalisation indisponible."


    lieux = geo.get("results")
    if not lieux:                  
        return f"Can't find city : {city}"
    lieu = lieux[0]
    try:
        meteo = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lieu["latitude"],
                "longitude": lieu["longitude"],
                "current_weather": True,
                "timezone": "Europe/Paris",
            },
            timeout=10,
        ).json()
    except requests.HTTPError:
        return "Weather service unavailable."


    return f"Weather in {city}: {meteo['current_weather']['temperature']}°C."