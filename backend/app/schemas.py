from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class User(UserCreate):
    id: int