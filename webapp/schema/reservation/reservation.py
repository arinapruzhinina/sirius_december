from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Общая модель
class ReservationRead(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    date_reserv: datetime
    guest_count: int
    status: bool
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Модель для создания
class ReservationCreate(BaseModel):
    user_id: Optional[int]
    restaurant_id: int
    date_reserv: datetime
    guest_count: int
    status: Optional[bool] = False
    comment: Optional[str] = None


# Модель для обновления
class ReservationUpdate(BaseModel):
    user_id: Optional[int] = None
    restaurant_id: Optional[int] = None
    date_reserv: Optional[datetime] = None
    guest_count: Optional[int] = None
    status: Optional[bool] = None
    comment: Optional[str] = None
