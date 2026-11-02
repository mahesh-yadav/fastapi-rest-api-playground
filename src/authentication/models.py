from typing import Literal

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__: str = "users"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: str = Field(default="USER")


class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)


class UserUpdate(SQLModel):
    email: EmailStr | None = None


class UserResponse(SQLModel):
    id: int
    email: EmailStr
    role: Literal["USER", "ADMIN"]
