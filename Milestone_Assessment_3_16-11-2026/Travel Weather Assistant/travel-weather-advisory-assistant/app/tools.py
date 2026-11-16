import requests
from rapidfuzz import process, fuzz
from langchain_core.tools import tool
from app.database import get_trip_by_id

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CITY_ALIASES = {
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "jaipur": "Jaipur",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "kochi": "Kochi",
    "cochin": "Kochi",
    "thiruvananthapuram": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram",
}


def get_coordinates(city: str):

    city = city.strip()

    if not city:
        return None

    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=15
    )

    response.raise_for_status()
    data = response.json()

    results = data.get("results")

    matched_city = city

    if not results:

        match = process.extractOne(city.lower(),list(CITY_ALIASES.keys()),scorer=fuzz.ratio)

        if not match or match[1] < 80:
            return None

        matched_city = CITY_ALIASES[match[0]]

        # Search again using corrected city name
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": matched_city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=15
        )

        response.raise_for_status()
        results = response.json().get("results")

    if not results:
        return None

    location = results[0]

    return {
        "name": location["name"],
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "matched_input": city
    }

def get_weather(city: str, start_date: str = None,
                end_date: str = None):
    """
    Retrieve weather forecast for a city.
    Optionally specify a travel date range.
    """

    location = get_coordinates(city)

    if not location:
        return {"error": f"Location not found: {city}"}

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto"
    }

    # Apply requested travel dates
    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    return {
        "location": location,
        "daily_forecast": data.get("daily", {}),
        "units": data.get("daily_units", {})
    }


def get_weather(city: str, start_date: str = None,
                end_date: str = None):
    """
    Retrieve weather forecast for a city.
    Optionally specify a travel date range.
    """

    location = get_coordinates(city)

    if not location:
        return {"error": f"Location not found: {city}"}

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto"
    }

    # Apply requested travel dates
    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    return {
        "location": location,
        "daily_forecast": data.get("daily", {}),
        "units": data.get("daily_units", {})
    }


@tool
def get_weather_tool(city:str,start_date:str=None,end_date:str=None)->str:
    """
    Get weather forecast for a city.
    Use this when the employee asks about weather, temperature,
    rainfall or travel weather conditions.
    """
    result=get_weather(city,start_date,end_date)
    return str(result)

@tool
def get_trip_tool(trip_id:int)->str:
    """
    Retrieve registered business trip details using trip ID.
    Use this when the employee asks about a previously registered trip.
    """
    trip=get_trip_by_id(trip_id)
    if not trip:
        return f"Trip not found: {trip_id}"
    return str(trip)

tools=[get_weather_tool,get_trip_tool]