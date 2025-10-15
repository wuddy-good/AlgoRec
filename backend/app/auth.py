from datetime import datetime, timedelta
from jose import jwt, JWTError

# Creating a JWT token
SECRET_KEY = "секрет_строка_для_подписи" 
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc)() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #
    to_encode.update({"exp": expire}) 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 