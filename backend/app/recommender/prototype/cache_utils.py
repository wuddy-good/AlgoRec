import pickle
import hashlib
from pathlib import Path
from src.config import DATA_DIR, CACHE_DIR
from src.utils import logger

def get_data_hash():
    """
    Обчислює хеш-суму вмісту файлів даних для перевірки валідності кешу.
    """
    hash_object = hashlib.sha256()
    for file_path in sorted(DATA_DIR.glob("*.csv")):
        with open(file_path, 'rb') as f:
            # Читаємо файл частинами, щоб не завантажувати великі файли повністю в пам'ять
            for chunk in iter(lambda: f.read(4096), b""):
                hash_object.update(chunk)
    return hash_object.hexdigest()

def load_cache(cache_path: Path, force_recompute: bool = False):
    """
    Завантажує об'єкт з кешу, якщо він валідний.

    :param cache_path: Шлях до файлу кешу.
    :param force_recompute: Примусово ігнорувати кеш.
    :return: Завантажений об'єкт або None, якщо кеш невалідний/відсутній.
    """
    if force_recompute:
        logger.info(f"Примусовий перерахунок. Ігноруємо кеш: {cache_path.name}")
        return None

    if not cache_path.exists():
        logger.info(f"Кеш не знайдено: {cache_path.name}")
        return None

    try:
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)
            data_hash = cache_data.get('hash')
            data = cache_data.get('data')
            
            current_hash = get_data_hash()
            
            if data_hash == current_hash:
                logger.info(f"Кеш валідний. Завантажено: {cache_path.name}")
                return data
            else:
                logger.warning(f"Кеш невалідний (змінилися вхідні дані). Перераховуємо: {cache_path.name}")
                return None
    except Exception as e:
        logger.error(f"Помилка при завантаженні кешу {cache_path.name}: {e}")
        return None

def save_cache(cache_path: Path, data):
    """
    Зберігає об'єкт у кеш разом із хеш-сумою вхідних даних.

    :param cache_path: Шлях до файлу кешу.
    :param data: Об'єкт для збереження.
    """
    try:
        data_hash = get_data_hash()
        cache_data = {'hash': data_hash, 'data': data}
        
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        logger.info(f"Дані успішно збережено в кеш: {cache_path.name}")
    except Exception as e:
        logger.error(f"Помилка при збереженні кешу {cache_path.name}: {e}")
