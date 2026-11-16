from app.tools import get_coordinates,get_weather
location=get_coordinates("Malapuram")
print(location)

weather=get_weather("Banglore","2026-11-18","2026-11-20")
print(weather)