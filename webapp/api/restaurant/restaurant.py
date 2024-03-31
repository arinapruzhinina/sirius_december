from typing import List

import orjson
from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.api.restaurant.router import restaurant_router
from webapp.cache.key_builder import get_restaurant_by_id_cache, get_restaurant_menu_by_id_cache, get_restaurants_cache
from webapp.crud.dish import get_dishes_by_restaurant_id_and_category
from webapp.crud.restaurant import (
    create_restaurant,
    delete_restaurant,
    get_restaurant,
    get_restaurants,
    update_restaurant,
)
from webapp.db.postgres import get_session
from webapp.db.redis import get_redis
from webapp.models.sirius.dish import DishCategory
from webapp.schema.restaurant.dish import DishRead
from webapp.schema.restaurant.restaurant import RestaurantCreate, RestaurantRead, RestaurantUpdate
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@restaurant_router.post(
    '/',
    response_model=RestaurantRead,
    tags=['Restaurants'],
    status_code=status.HTTP_201_CREATED,
    response_class=ORJSONResponse,
)
async def create_new_restaurant(
    restaurant_data: RestaurantCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] == 'Администратор':
        try:
            restaurant = await create_restaurant(session=session, restaurant_data=restaurant_data)

            cache_key = get_restaurants_cache()
            await redis.delete(cache_key)

            return restaurant
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')


@restaurant_router.get(
    '/{restaurant_id}', response_model=RestaurantRead, tags=['Restaurants'], response_class=ORJSONResponse
)
async def get_single_restaurant(
    restaurant_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    try:
        cache_key = get_restaurant_by_id_cache(restaurant_id=restaurant_id)
        cached_restaurant = await redis.get(cache_key)
        if cached_restaurant:
            if cached_restaurant == b'{}':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Запись о ресторане не найдена')
            return orjson.loads(cached_restaurant)
        else:
            restaurant = await get_restaurant(session=session, restaurant_id=restaurant_id)
            if restaurant is None:
                await redis.set(cache_key, b'{}', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Запись о ресторане не найдена')
            await redis.set(cache_key, orjson.dumps(restaurant.model_dump()), ex=3600)
            return restaurant
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@restaurant_router.get(
    '/{restaurant_id}/menu', response_model=List[DishRead], tags=['Restaurants'], response_class=ORJSONResponse
)
async def get_dishes_for_restaurant(
    restaurant_id: int,
    category: DishCategory = Query(None, description='Фильтр по категории блюд'),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    try:
        cache_key = get_restaurant_menu_by_id_cache(restaurant_id=restaurant_id, category=category)
        cached_menu = await redis.get(cache_key)
        if cached_menu:
            if cached_menu == b'[]':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Меню ресторана не найдено')
            return orjson.loads(cached_menu)
        else:
            menu = await get_dishes_by_restaurant_id_and_category(
                session=session, restaurant_id=restaurant_id, category=category
            )
            if menu is None:
                await redis.set(cache_key, b'[]', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Меню ресторана не найдено')
            await redis.set(cache_key, orjson.dumps([dish.model_dump() for dish in menu]), ex=3600)
            return menu
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@restaurant_router.get('/', response_model=List[RestaurantRead], tags=['Restaurants'], response_class=ORJSONResponse)
async def get_all_restaurants(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)):
    try:
        cache_key = get_restaurants_cache()
        cached_restaurants = await redis.get(cache_key)
        if cached_restaurants:
            if cached_restaurants == b'[]':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Список ресторанов не найден')
            return orjson.loads(cached_restaurants)
        else:
            restaurants = await get_restaurants(session=session)
            if restaurants is None:
                await redis.set(cache_key, b'[]', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Список ресторанов не найден')
            await redis.set(cache_key, orjson.dumps([restaurant.model_dump() for restaurant in restaurants]), ex=3600)
            return restaurants
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@restaurant_router.put(
    '/{restaurant_id}', response_model=RestaurantRead, tags=['Restaurants'], response_class=ORJSONResponse
)
async def update_existing_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] == 'Администратор':
        try:
            restaurant = await update_restaurant(
                session=session, restaurant_id=restaurant_id, restaurant_data=restaurant_data
            )
            if restaurant is None:
                return ORJSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND, content='Обновляемая запись о ресторане не найдена'
                )
            cache_key_restaurant_by_id = get_restaurant_by_id_cache(restaurant_id=restaurant_id)
            cache_key_restaurants = get_restaurants_cache()
            await redis.delete(cache_key_restaurant_by_id, cache_key_restaurants)
            return restaurant
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')


@restaurant_router.delete(
    '/{restaurant_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Restaurants'], response_class=ORJSONResponse
)
async def delete_existing_restaurant(
    restaurant_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] == 'Администратор':
        try:
            deleted_restaurant_id = await delete_restaurant(session=session, restaurant_id=restaurant_id)
            if deleted_restaurant_id is False:
                return ORJSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND, content='Удаляемая запись о ресторане не найдена'
                )
            cache_key_restaurant_by_id = get_restaurant_by_id_cache(restaurant_id=restaurant_id)
            cache_key_restaurants = get_restaurants_cache()
            await redis.delete(cache_key_restaurant_by_id, cache_key_restaurants)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')
