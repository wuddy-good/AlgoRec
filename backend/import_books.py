import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Book, Base

print("1. Імпорти завантажені")

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)
print("2a. Таблиці створені")

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("2. Підключення до БД створено")

print("1. Імпорти завантажені")

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("2. Підключення до БД створено")

def import_books(csv_file_path):
    print(f"3. Функкція запущена: {csv_file_path}")
    
    success_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='ISO-8859-1') as file:
            print("4. Файл відкрит успішно!")
            csv_reader = csv.DictReader(file, delimiter=';') 
            print("5. Починаємо зчитувати строки...")
            for row in csv_reader:
                try:
                    book = Book(
                        isbn=row['ISBN'].strip() if row['ISBN'] else None,
                        title=row['Book-Title'].strip() if row['Book-Title'] else 'Unknown',
                        author=row['Book-Author'].strip() if row['Book-Author'] else None,
                        year=int(row['Year-Of-Publication']) if row['Year-Of-Publication'] and row['Year-Of-Publication'].strip() else None,
                        publisher=row['Publisher'].strip() if row['Publisher'] else None,
                        image_url_s=row['Image-URL-S'].strip() if row['Image-URL-S'] else None,
                        image_url_m=row['Image-URL-M'].strip() if row['Image-URL-M'] else None,
                        image_url_l=row['Image-URL-L'].strip() if row['Image-URL-L'] else None
                    )
                    
                    session.add(book)
                    success_count += 1
                    
                    if success_count % 100 == 0:
                        session.commit()
                        print(f"✅ Імпортовано {success_count} книг...")
                        
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"❌ Помилка при імпорті книги: {e}")
                    session.rollback()
                    continue
            
            session.commit()
            print("6. Фінальний комміт виконано.")
            
    except FileNotFoundError:
        print(f"❌ Помилка: {csv_file_path} не знайдено!")
        return
    except Exception as e:
        print(f"❌ Помилка при відкритті файла: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'='*50}")
    print(f"✅ Імпорт закінчено!")
    print(f"{'='*50}")
    print(f"Успішно імпортовано: {success_count} книг")
    print(f"Помилок: {error_count}")
    print(f"{'='*50}")
    
    session.close()

print("7. Функция імпорту визначена")

if __name__ == "__main__":
    print("8. Запускаємо імпорт...\n")
    import_books("data/books.csv")
    print("\n9. Скрипт закінчено!")