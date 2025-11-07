import logging
import sys
from src.config import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT, DEFAULT_LOG_LEVEL, DEBUG_LOG_LEVEL

def setup_logging(debug_mode=False):
    """
    Налаштовує логування для програми.

    :param debug_mode: Якщо True, встановлює рівень логування DEBUG, інакше INFO.
    """
    log_level = DEBUG_LOG_LEVEL if debug_mode else DEFAULT_LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Невірний рівень логування: {log_level}')

    # Створення логера
    logger = logging.getLogger('AlgoRec')
    logger.setLevel(numeric_level)

    # Запобігання багаторазовому додаванню обробників
    if not logger.handlers:
        # Обробник для STDOUT
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(numeric_level)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Обробник для файлу
        fh = logging.FileHandler(LOG_FILE, mode='a')
        fh.setLevel(numeric_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Налаштування логування для сторонніх бібліотек
    logging.getLogger('pandas').setLevel(logging.WARNING)
    logging.getLogger('sklearn').setLevel(logging.WARNING)
    logging.getLogger('numexpr').setLevel(logging.WARNING)

    logger.info(f"Логування налаштовано. Рівень: {log_level}")
    return logger

# Ініціалізація логера для використання в інших модулях
logger = setup_logging()
