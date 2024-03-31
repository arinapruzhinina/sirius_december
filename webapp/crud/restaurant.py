from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.models.sirius.restaurant import Restaurant
from webapp.schema.restaurant.restaurant import RestaurantCreate, RestaurantRead, RestaurantUpdate


async def create_restaurant(session: AsyncSession, restaurant_data: RestaurantCreate) -> RestaurantRead | None:
    restaurant = Restaurant(**restaurant_data.model_dump())
    session.add(restaurant)
    await session.commit()
    await session.refresh(restaurant)
    return RestaurantRead.model_validate(restaurant)


async def get_restaurant(session: AsyncSession, restaurant_id: int) -> RestaurantRead | None:
    statement = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await session.execute(statement)
    restaurant = result.scalar()
    if not restaurant:
        return None

    return RestaurantRead.model_validate(restaurant)


async def get_restaurants(session: AsyncSession) -> List[RestaurantRead] | None:
    statement = select(Restaurant)
    result = await session.execute(statement)
    restaurants = result.scalars().all()
    if not restaurants:
        return None

    return [RestaurantRead.model_validate(restaurant) for restaurant in restaurants]


async def update_restaurant(
    session: AsyncSession, restaurant_id: int, restaurant_data: RestaurantUpdate
) -> RestaurantRead | None:
    statement = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await session.execute(statement)
    restaurant = result.scalar()
    if not restaurant:
        return None

    for field, value in restaurant_data.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)

    await session.commit()
    await session.refresh(restaurant)
    return RestaurantRead.model_validate(restaurant)


async def delete_restaurant(session: AsyncSession, restaurant_id: int) -> bool:
    statement = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await session.execute(statement)
    restaurant = result.scalar()
    if not restaurant:
        return False

    await session.delete(restaurant)
    await session.commit()
    return True
