from typing import List

import orjson
from fastapi import Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.restaurant.router import dish_router
from webapp.cache.key_builder import get_dish_by_id_cache, get_dishes_cache, get_restaurant_menu_by_id_cache
from webapp.crud.dish import create_dish, delete_dish, get_dish, get_dishes, update_dish
from webapp.db.postgres import get_session
from webapp.db.redis import get_redis
from webapp.models.sirius.dish import DishCategory
from webapp.schema.restaurant.dish import DishCreate, DishRead, DishUpdate
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@dish_router.post(
    '/', response_model=DishRead, status_code=status.HTTP_201_CREATED, tags=['Dishes'], response_class=ORJSONResponse
)
async def create_dish_endpoint(
    dish_data: DishCreate,
    session: AsyncSession = Depends(get_session),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
    redis: Redis = Depends(get_redis),
):
    if current_user['role'] in ['Администратор', 'Сотрудник']:
        try:
            dish = await create_dish(session=session, dish_data=dish_data)

            cache_key_dishes = get_dishes_cache()
            cache_key_with_category = get_dishes_cache(category=dish_data.category)
            cache_key_restaurant_menu = get_restaurant_menu_by_id_cache(restaurant_id=dish.restaurant_id)
            await redis.delete(cache_key_dishes, cache_key_with_category, cache_key_restaurant_menu)

            return dish
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нет доступа для выполнения этой операции')


@dish_router.get('/{dish_id}', response_model=DishRead, tags=['Dishes'], response_class=ORJSONResponse)
async def get_dish_endpoint(
    dish_id: int, session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
):
    try:
        cache_key_dish_by_id = get_dish_by_id_cache(dish_id=dish_id)
        cached_dish = await redis.get(cache_key_dish_by_id)
        if cached_dish:
            if cached_dish == b'{}':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Блюдо не найдено')
            return orjson.loads(cached_dish)
        else:
            dish = await get_dish(session=session, dish_id=dish_id)
            if dish is None:
                await redis.set(cache_key_dish_by_id, b'{}', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Блюдо не найдено')
            await redis.set(cache_key_dish_by_id, orjson.dumps(dish.model_dump()), ex=3600)
            return dish
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@dish_router.get('/', response_model=List[DishRead], tags=['Dishes'], response_class=ORJSONResponse)
async def get_dishes_endpoint(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    category: DishCategory = Query(None, description='Фильтр по категории блюд'),
):
    try:
        cache_key_dishes = get_dishes_cache(category=category)
        cached_dishes = await redis.get(cache_key_dishes)
        if cached_dishes:
            if cached_dishes == b'[]':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Блюда не найдены')
            return orjson.loads(cached_dishes)
        else:
            dishes = await get_dishes(session=session, category=category)
            if dishes is None:
                await redis.set(cache_key_dishes, b'[]', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Блюда не найдены')
            await redis.set(cache_key_dishes, orjson.dumps([dish.model_dump() for dish in dishes]), ex=3600)
            return dishes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@dish_router.put('/{dish_id}', response_model=DishRead, tags=['Dishes'], response_class=ORJSONResponse)
async def update_dish_endpoint(
    dish_id: int,
    dish_data: DishUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] in ['Администратор', 'Сотрудник']:
        try:
            dish = await update_dish(session=session, dish_id=dish_id, dish_data=dish_data)
            if dish is None:
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Обновляемое блюдо не найдено')
            cache_key_dish_by_id = get_dish_by_id_cache(dish_id=dish_id)
            cache_key_restaurant_menu = get_restaurant_menu_by_id_cache(restaurant_id=dish.restaurant_id)
            await redis.delete(cache_key_dish_by_id, cache_key_restaurant_menu)
            return dish
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')


@dish_router.delete(
    '/{dish_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Dishes'],
    response_class=ORJSONResponse,
)
async def delete_dish_endpoint(
    dish_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] in ['Администратор', 'Сотрудник']:
        try:
            dish = await get_dish(session=session, dish_id=dish_id)
            deleted_dish = await delete_dish(session=session, dish_id=dish_id)
            if deleted_dish is False:
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Удаляемое блюдо не найдено')
            cache_key_dishes = get_dishes_cache()
            cache_key_dish_by_id = get_dish_by_id_cache(dish_id=dish_id)
            cache_key_with_category = get_dishes_cache(category=dish.category)
            cache_key_restaurant_menu = get_restaurant_menu_by_id_cache(restaurant_id=dish.restaurant_id)
            await redis.delete(
                cache_key_dishes, cache_key_dish_by_id, cache_key_with_category, cache_key_restaurant_menu
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')
