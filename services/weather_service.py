import aiohttp
from core.config import config
from core.logger import logger


async def get_weather(city: str, session: aiohttp.ClientSession = None) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.WEATHER_API_KEY}&units=metric"

    # Используем переданную сессию или создаем временную (для обратной совместимости)
    _session = session or aiohttp.ClientSession()
    try:
        async with _session.get(url) as response:
            if response.status != 200:
                logger.error(f"Weather API error: {response.status}")
                raise Exception(f"Failed to fetch weather: {response.status}")
            
            data = await response.json()
            return {
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"]
            }
    finally:
        if session is None:
            await _session.close()