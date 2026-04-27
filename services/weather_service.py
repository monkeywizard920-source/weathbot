import aiohttp
from core.config import config
from core.logger import logger


async def get_weather(city: str) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.WEATHER_API_KEY}&units=metric"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "temp": data["main"]["temp"],
                    "description": data["weather"][0]["description"]
                }
            else:
                logger.error(f"Failed to fetch weather data: {response.status}")
                raise Exception("Failed to fetch weather data")