from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str


class UserRead(BaseModel):
    id: int
    username: str
    phone: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    phone: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
