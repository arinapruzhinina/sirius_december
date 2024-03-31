from typing import Optional

from pydantic import BaseModel, ConfigDict


# Основная модель
class RestaurantRead(BaseModel):
    id: int
    name: str
    address: str
    description: str

    model_config = ConfigDict(from_attributes=True)


# Модель для создания
class RestaurantCreate(BaseModel):
    name: str
    address: str
    description: str


# Модель для обновления
class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
