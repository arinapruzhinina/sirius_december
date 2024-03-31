from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.models.sirius.dish import Dish, DishCategory
from webapp.schema.restaurant.dish import DishCreate, DishRead, DishUpdate


async def create_dish(session: AsyncSession, dish_data: DishCreate) -> DishRead | None:
    dish = Dish(**dish_data.model_dump())
    session.add(dish)
    await session.commit()
    await session.refresh(dish)
    return DishRead.model_validate(dish)


async def get_dish(session: AsyncSession, dish_id: int) -> DishRead | None:
    statement = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(statement)
    dish = result.scalar()
    if not dish:
        return None

    return DishRead.model_validate(dish)


async def get_dishes(session: AsyncSession, category: DishCategory = None) -> List[DishRead] | None:
    statement = select(Dish)
    if category:
        statement = statement.where(Dish.category == category)
    result = await session.execute(statement)
    dishes = result.scalars().all()
    if not dishes:
        return None

    return [DishRead.model_validate(dish) for dish in dishes]


async def update_dish(session: AsyncSession, dish_id: int, dish_data: DishUpdate) -> DishRead | None:
    statement = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(statement)
    dish = result.scalar()
    if not dish:
        return None

    for field, value in dish_data.model_dump(exclude_unset=True).items():
        setattr(dish, field, value)

    await session.commit()
    await session.refresh(dish)
    return DishRead.model_validate(dish)


async def delete_dish(session: AsyncSession, dish_id: int) -> bool:
    statement = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(statement)
    dish = result.scalar()
    if not dish:
        return False

    await session.delete(dish)
    await session.commit()
    return True


async def get_dishes_by_restaurant_id_and_category(
    session: AsyncSession, restaurant_id: int, category: DishCategory = None
) -> List[DishRead] | None:
    filters = [Dish.restaurant_id == restaurant_id]
    if category:
        filters.append(Dish.category == category)

    statement = select(Dish).where(and_(*filters))
    result = await session.execute(statement)
    dishes = result.scalars().all()
    if not dishes:
        return None

    return [DishRead.model_validate(dish) for dish in dishes]
