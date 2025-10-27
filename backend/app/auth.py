from datetime import datetime, timedelta, timezone
from jose import jwt  # JWTError можна додати, якщо треба для обробки помилок

# налаштування JWT
SECRET_KEY = "5ffded193d5ee5c8913c03abd335ee7e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """Створює JWT-токен з терміном дії."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
