import csv
from app.database import SessionLocal
from app.models import User, Rating, BotUser, Book

def import_users_csv(csv_file_path: str, delimiter=';'):
    """
    Імпорт користувачів з users.csv
    Очікуваний формат CSV: User-ID, Location, Age
    """
    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            
            bot_users_added = 0
            
            for row in csv_reader:
                try:
                    user_id = int(row['User-ID'])
                    location = row.get('Location', '').strip() or None
                    age_str = row.get('Age', '').strip()
                    
                    # Обробка віку
                    age = None
                    if age_str and age_str.lower() != 'null':
                        try:
                            age = int(float(age_str))
                        except ValueError:
                            age = None
                    
                    # Створюємо bot user
                    bot_user = BotUser(
                        id=user_id,
                        location=location,
                        age=age
                    )
                    
                    db.add(bot_user)
                    bot_users_added += 1
                    
                    # Commit кожні 1000 записів для продуктивності
                    if bot_users_added % 1000 == 0:
                        db.commit()
                        print(f"Імпортовано {bot_users_added} користувачів...")
                        
                except Exception as e:
                    print(f"Помилка при обробці рядка {row}: {e}")
                    db.rollback()  # Додав rollback для кожної помилки
                    continue
            
            db.commit()
            print(f"✅ Успішно імпортовано {bot_users_added} користувачів з {csv_file_path}")
            
    except Exception as e:
        print(f"❌ Помилка при імпорті користувачів: {e}")
        db.rollback()
    finally:
        db.close()


def import_ratings_csv(csv_file_path: str, delimiter=';'):
    """
    Імпорт рейтингів з ratings.csv
    Очікуваний формат CSV: User-ID, ISBN, Book-Rating
    """
    db = SessionLocal()
    try:
        # Створюємо мапінг ISBN -> book_id
        books = db.query(Book).all()
        isbn_to_id = {book.isbn: book.id for book in books if book.isbn}
        print(f"Знайдено {len(isbn_to_id)} книг у базі")
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            
            ratings_added = 0
            skipped = 0
            
            for row in csv_reader:
                try:
                    user_id = int(row['User-ID'])
                    isbn = row['ISBN'].strip()
                    rating_value = int(row['Book-Rating'])
                    
                    # Знаходимо book_id за ISBN
                    book_id = isbn_to_id.get(isbn)
                    
                    if book_id is None:
                        skipped += 1
                        continue
                    
                    # Створюємо рейтинг
                    rating = Rating(
                        user_id=user_id,
                        book_id=book_id,
                        rating=rating_value,
                        is_bot=True
                    )
                    
                    db.add(rating)
                    ratings_added += 1
                    
                    # Commit кожні 1000 записів
                    if ratings_added % 1000 == 0:
                        db.commit()
                        print(f"Імпортовано {ratings_added} рейтингів...")
                        
                except Exception as e:
                    print(f"Помилка при обробці рядка {row}: {e}")
                    continue
            
            db.commit()
            print(f"✅ Успішно імпортовано {ratings_added} рейтингів")
            print(f"⚠️ Пропущено {skipped} рейтингів (книги не знайдені)")
            
    except Exception as e:
        print(f"❌ Помилка при імпорті рейтингів: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Початок імпорту даних...")
    
    # Імпорт користувачів
    import_users_csv('data/users.csv')
    
    # Імпорт рейтингів (розкоментуй після успішного імпорту користувачів)
    # import_ratings_csv('data/ratings.csv')
    
    print("Імпорт завершено!")