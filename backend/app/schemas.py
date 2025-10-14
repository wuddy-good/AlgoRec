from pydantic import BaseModel

# Schema for user registration
class UserLogin(BaseModel):
    email: str
    password: str