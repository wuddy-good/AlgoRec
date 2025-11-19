import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.base import Base

# Используем PostgreSQL (из Docker или локально)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:Afds42ASfdsf@localhost:5432/mydb"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()