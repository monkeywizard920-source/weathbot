import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger("discord_bot")
    logger.setLevel(logging.INFO)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Логирование в файл
    file_handler = RotatingFileHandler(
        'bot.log', maxBytes=1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()