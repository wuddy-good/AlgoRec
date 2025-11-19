import csv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Book, Rating


def import_ratings_csv(csv_file_path: str, delimiter=';'):
    """
    Імпорт рейтингів з ratings.csv
    Очікуваний формат CSV: User-ID, ISBN, Book-Rating
    """
    db: Session = SessionLocal()

    try:
        # Створюємо мапінг ISBN -> book_id
        books = db.query(Book).all()
        isbn_to_id = {book.isbn: book.id for book in books if book.isbn}
        print(f"Знайдено {len(isbn_to_id)} книг у базі")

        with open(csv_file_path, 'r', encoding='latin-1') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)

            ratings_added = 0
            skipped = 0

            for row in csv_reader:
                try:
                    user_id = int(row['User-ID'])
                    isbn = row['ISBN'].strip()
                    rating_value = int(row['Book-Rating'])

                    if not isbn:
                        skipped += 1
                        continue

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
            print(f"⚠️ Пропущено {skipped} рейтингів (книги не знайдені або ISBN порожній)")

    except Exception as e:
        print(f"❌ Помилка при імпорті рейтингів: {e}")
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    print("Початок імпорту рейтингів...")

    import_ratings_csv('data/ratings.csv')

    print("Імпорт завершено!")
