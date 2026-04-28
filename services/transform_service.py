import re
from core.config import config
from core.logger import logger


async def transform_text(text: str) -> str:
    # Удаление ссылок
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Очистка лишних пробелов после удаления ссылок
    text = re.sub(r' +', ' ', text).strip()

    # Замена запрещённых слов (регистронезависимо)
    for bad_word, good_word in config.FORBIDDEN_WORDS.items():
        pattern = re.compile(re.escape(bad_word), re.IGNORECASE)
        text = pattern.sub(good_word, text)

    # Заглушка для функции перефразирования
    logger.info("Text transformed successfully")
    return text