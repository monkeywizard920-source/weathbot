import aiohttp
from core.config import config
from core.logger import logger


async def translate_text(text: str, target_lang: str) -> str:
    url = "https://api-free.deepl.com/v2/translate"
    headers = {
        "Authorization": f"DeepL-Auth-Key {config.TRANSLATE_API_KEY}"
    }
    data = {
        "text": text,
        "target_lang": target_lang.upper()  # DeepL использует верхний регистр для кодов языков
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                data = await response.json()
                return data["translations"][0]["text"]
            else:
                logger.error(f"Failed to translate text: {response.status}")
                raise Exception("Failed to translate text")