"""
Модуль seeder.py - Завантаження даних з CSV у таблицю books
Адаптовано під реальну структуру БД
"""

import pandas as pd
import logging
from sqlalchemy.orm import Session
from pathlib import Path
from app.models import Book, Rating, BotUser
from app.database import SessionLocal
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_books_from_csv(db: Session, csv_path: str = "app/recommender/data/items.csv"):
    """
    Завантажує книги з CSV файлу в таблицю books.
    
    Мапінг CSV -> БД:
    - CSV 'id' -> БД 'id'
    - CSV 'title' -> БД 'title'
    - CSV 'author_director' -> БД 'author'
    - CSV 'release_year' -> БД 'year'
    - CSV 'description' -> використовується для генерації publisher (опціонально)
    
    Поля, яких немає в CSV:
    - 'isbn' -> генеруємо фейковий або залишаємо NULL
    - 'publisher' -> витягуємо з description або генеруємо
    - 'image_url_s/m/l' -> залишаємо NULL або генеруємо placeholder
    
    :param db: Сесія SQLAlchemy
    :param csv_path: Шлях до CSV файлу
    """
    logger.info(f"Початок завантаження книг з {csv_path}...")
    
    # Перевірка існування файлу
    if not Path(csv_path).exists():
        logger.error(f"Файл {csv_path} не знайдено!")
        return
    
    # Читаємо CSV
    df = pd.read_csv(csv_path)
    logger.info(f"Прочитано {len(df)} записів з CSV")
    
    # Фільтруємо тільки книги (якщо в CSV є інші типи)
    if 'item_type' in df.columns:
        df = df[df['item_type'] == 'book']
        logger.info(f"Після фільтрації за типом 'book': {len(df)} записів")
    
    books_added = 0
    books_skipped = 0
    
    for _, row in df.iterrows():
        try:
            # Перевіряємо, чи книга вже існує
            existing_book = db.query(Book).filter(Book.id == row['id']).first()
            if existing_book:
                logger.debug(f"Книга з ID {row['id']} вже існує, пропускаємо")
                books_skipped += 1
                continue
            
            # Генерація ISBN (фейковий, якщо потрібно)
            # Формат: 978-0-XXX-XXXXX-X (13 цифр)
            isbn = f"978-0-{random.randint(100, 999)}-{random.randint(10000, 99999)}-{random.randint(0, 9)}"
            
            # Витягуємо publisher з description або генеруємо
            publisher = None
            if pd.notna(row.get('description', None)):
                # Можна спробувати витягти видавництво з опису
                # Для простоти просто беремо перше слово
                desc_words = str(row['description']).split()
                if len(desc_words) > 2:
                    publisher = " ".join(desc_words[-2:])  # Останні 2 слова як "видавництво"
            
            if not publisher or publisher == "":
                publisher = f"Видавництво-{random.randint(1, 100)}"
            
            # Генерація placeholder URL для зображень
            placeholder_base = "https://via.placeholder.com"
            image_url_s = f"{placeholder_base}/150x200?text={row['title'][:10]}"
            image_url_m = f"{placeholder_base}/300x400?text={row['title'][:10]}"
            image_url_l = f"{placeholder_base}/600x800?text={row['title'][:10]}"
            
            # Створюємо об'єкт Book
            book = Book(
                id=int(row['id']),
                isbn=isbn,
                title=str(row['title']),
                author=str(row['author_director']) if pd.notna(row.get('author_director')) else "Unknown Author",
                year=int(row['release_year']) if pd.notna(row.get('release_year')) else 2000,
                publisher=publisher,
                image_url_s=image_url_s,
                image_url_m=image_url_m,
                image_url_l=image_url_l
            )
            
            db.add(book)
            books_added += 1
            
            # Комітимо кожні 100 записів для продуктивності
            if books_added % 100 == 0:
                db.commit()
                logger.info(f"Додано {books_added} книг...")
        
        except Exception as e:
            logger.error(f"Помилка при обробці рядка {row.get('id', 'Unknown')}: {e}")
            db.rollback()
            continue
    
    # Фінальний коміт
    db.commit()
    
    logger.info(f"Завантаження завершено! Додано: {books_added}, Пропущено: {books_skipped}")


def seed_ratings_from_csv(db: Session, csv_path: str = "app/recommender/data/ratings.csv"):
    """
    Завантажує рейтинги з CSV файлу в таблицю ratings.
    
    Мапінг CSV -> БД:
    - CSV 'user_id' -> БД 'user_id'
    - CSV 'item_id' -> БД 'book_id' (КРИТИЧНО!)
    - CSV 'rating' -> БД 'rating'
    
    :param db: Сесія SQLAlchemy
    :param csv_path: Шлях до CSV файлу
    """
    logger.info(f"Початок завантаження рейтингів з {csv_path}...")
    
    if not Path(csv_path).exists():
        logger.error(f"Файл {csv_path} не знайдено!")
        return
    
    df = pd.read_csv(csv_path)
    logger.info(f"Прочитано {len(df)} рейтингів з CSV")
    
    ratings_added = 0
    ratings_skipped = 0
    
    for _, row in df.iterrows():
        try:
            # Перевіряємо, чи існує такий рейтинг
            existing_rating = db.query(Rating).filter(
                Rating.user_id == row['user_id'],
                Rating.book_id == row['item_id']  # item_id з CSV -> book_id в БД!
            ).first()
            
            if existing_rating:
                ratings_skipped += 1
                continue
            
            # Створюємо рейтинг
            rating = Rating(
                user_id=int(row['user_id']),
                book_id=int(row['item_id']),  # КРИТИЧНА АДАПТАЦІЯ!
                rating=int(row['rating']),
                is_bot=bool(row.get('is_bot', False)) if 'is_bot' in row else False
            )
            
            db.add(rating)
            ratings_added += 1
            
            if ratings_added % 500 == 0:
                db.commit()
                logger.info(f"Додано {ratings_added} рейтингів...")
        
        except Exception as e:
            logger.error(f"Помилка при обробці рейтингу: {e}")
            db.rollback()
            continue
    
    db.commit()
    logger.info(f"Завантаження рейтингів завершено! Додано: {ratings_added}, Пропущено: {ratings_skipped}")


def seed_bot_users_from_csv(db: Session, csv_path: str = "app/recommender/data/bot_users.csv"):
    """
    Завантажує bot користувачів з CSV файлу.
    
    :param db: Сесія SQLAlchemy
    :param csv_path: Шлях до CSV файлу
    """
    logger.info(f"Початок завантаження bot користувачів з {csv_path}...")
    
    if not Path(csv_path).exists():
        logger.warning(f"Файл {csv_path} не знайдено, пропускаємо")
        return
    
    df = pd.read_csv(csv_path)
    logger.info(f"Прочитано {len(df)} bot користувачів з CSV")
    
    users_added = 0
    
    for _, row in df.iterrows():
        try:
            existing_user = db.query(BotUser).filter(BotUser.id == row['user_id']).first()
            if existing_user:
                continue
            
            bot_user = BotUser(
                id=int(row['user_id']),
                location=str(row['location']) if pd.notna(row.get('location')) else None,
                age=int(row['age']) if pd.notna(row.get('age')) else None
            )
            
            db.add(bot_user)
            users_added += 1
        
        except Exception as e:
            logger.error(f"Помилка при обробці bot користувача: {e}")
            db.rollback()
            continue
    
    db.commit()
    logger.info(f"Завантаження bot користувачів завершено! Додано: {users_added}")


def main():
    """
    Головна функція для запуску seeder.
    Використання: python -m app.recommender.seeder
    """
    logger.info("=" * 60)
    logger.info("ЗАПУСК SEEDER ДЛЯ ЗАВАНТАЖЕННЯ ДАНИХ В БД")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Завантажуємо книги
        seed_books_from_csv(db, "app/recommender/data/items.csv")
        
        # 2. Завантажуємо bot користувачів (опціонально)
        seed_bot_users_from_csv(db, "app/recommender/data/bot_users.csv")
        
        # 3. Завантажуємо рейтинги
        seed_ratings_from_csv(db, "app/recommender/data/ratings.csv")
        
        logger.info("=" * 60)
        logger.info("SEEDER ЗАВЕРШИВ РОБОТУ УСПІШНО!")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Критична помилка при виконанні seeder: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()