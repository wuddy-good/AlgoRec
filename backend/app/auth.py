from datetime import datetime, timedelta, timezone
from jose import jwt  # JWTError можна додати, якщо треба для обробки помилок

# Set up
SECRET_KEY = "секрет_строка_для_подписи"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """Створює JWT-токен з терміном дії."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
