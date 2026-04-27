import re
from core.config import config
from core.logger import logger


async def transform_text(text: str) -> str:
    # Удаление ссылок
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Замена запрещённых слов
    for bad_word, good_word in config.FORBIDDEN_WORDS.items():
        text = text.replace(bad_word, good_word)

    # Заглушка для функции перефразирования
    logger.info("Text transformed successfully")
    return text