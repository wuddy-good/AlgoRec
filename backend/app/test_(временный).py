from passlib.context import CryptContext

# создаём объект для хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# тестовый пароль
plain_password = "mypassword123"

# создаём хэш
hashed_password = pwd_context.hash(plain_password)
print("Хэш пароля:", hashed_password)

# проверяем совпадение
is_valid = pwd_context.verify(plain_password, hashed_password)
print("Проверка пароля:", is_valid)
# проверяем с неправильным паролем
is_valid_wrong = pwd_context.verify("wrongpassword", hashed_password)
print("Проверка неправильного пароля:", is_valid_wrong)
