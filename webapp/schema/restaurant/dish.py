from typing import Optional

from pydantic import BaseModel, ConfigDict

from webapp.models.sirius.dish import DishCategory


# Общая модель
class DishRead(BaseModel):
    id: Optional[int] = None
    restaurant_id: int
    category: DishCategory
    dish_name: str
    description: str
    price: float

    model_config = ConfigDict(from_attributes=True)


# Модель для создания
class DishCreate(BaseModel):
    restaurant_id: int
    category: DishCategory
    dish_name: str
    description: str
    price: float


# Модель для обновления
class DishUpdate(BaseModel):
    restaurant_id: Optional[int] = None
    category: Optional[DishCategory] = None
    dish_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
