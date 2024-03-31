import enum

from sqlalchemy import ForeignKey, Integer, String, DECIMAL
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import DEFAULT_SCHEMA, Base


class DishCategory(str, enum.Enum):
    APPETIZER = 'Закуска'
    MAIN_COURSE = 'Основное блюдо'
    DESSERT = 'Десерт'
    SOUP = 'Суп'
    SALAD = 'Салат'
    HOT_DRINK = 'Горячий напиток'
    COLD_DRINK = 'Холодный напиток'


DishCategoryType: ENUM = ENUM(
    DishCategory,
    name='dish_category',
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class Dish(Base):
    __tablename__ = 'dish'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{DEFAULT_SCHEMA}.restaurant.id'))
    category: Mapped[ENUM] = mapped_column(DishCategoryType)
    dish_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2))

    restaurant = relationship('Restaurant', back_populates='menu')
