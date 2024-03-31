import orjson
from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.restaurant.router import reservation_router
from webapp.cache.key_builder import (
    get_reservation_by_id_cache,
    get_reservations_cache,
    get_user_reservations_by_id_cache,
)
from webapp.crud.reservation import (
    create_reservation,
    delete_reservation,
    get_reservation,
    get_reservations,
    update_reservation,
)
from webapp.db.postgres import get_session
from webapp.db.redis import get_redis
from webapp.schema.reservation.reservation import ReservationCreate, ReservationRead, ReservationUpdate
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@reservation_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=ReservationRead,
    tags=['Reservations'],
    response_class=ORJSONResponse,
)
async def create_reservation_endpoint(
    reservation_data: ReservationCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    try:
        if reservation_data.user_id == 0:
            reservation_data.user_id = current_user['user_id']
        reservation = await create_reservation(session=session, reservation_data=reservation_data)
        cache_key_reservations = get_reservations_cache(restaurant_id=reservation_data.restaurant_id)
        cache_key_reservation_by_id = get_reservation_by_id_cache(reservation_id=reservation.id)
        cache_key_user_reservations = get_user_reservations_by_id_cache(user_id=reservation.user_id)
        await redis.delete(cache_key_reservations, cache_key_reservation_by_id, cache_key_user_reservations)
        return reservation
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@reservation_router.get(
    '/{reservation_id}',
    response_model=ReservationRead,
    tags=['Reservations'],
    response_class=ORJSONResponse,
)
async def read_reservation_endpoint(
    reservation_id: int, session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
):
    try:
        cache_key_reservation_by_id = get_reservation_by_id_cache(reservation_id=reservation_id)
        cached_reservation = await redis.get(cache_key_reservation_by_id)
        if cached_reservation:
            if cached_reservation == b'{}':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Запись о бронировании не найдена')
            return orjson.loads(cached_reservation)
        else:
            reservation = await get_reservation(session=session, reservation_id=reservation_id)
            if reservation is None:
                await redis.set(cache_key_reservation_by_id, b'{}', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Запись о бронировании не найдена')
            await redis.set(cache_key_reservation_by_id, orjson.dumps(reservation.model_dump()), ex=3600)
            return reservation
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@reservation_router.get(
    '/{restaurant_id}', response_model=list[ReservationRead], tags=['Reservations'], response_class=ORJSONResponse
)
async def read_reservations_endpoint(
    restaurant_id: int, session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
):
    try:
        cache_key_reservations = get_reservations_cache(restaurant_id=restaurant_id)
        cached_reservations = await redis.get(cache_key_reservations)
        if cached_reservations:
            if cached_reservations == b'[]':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Записи о бронировании не найдены')
            return orjson.loads(cached_reservations)
        else:
            reservations = await get_reservations(session=session, restaurant_id=restaurant_id)
            if reservations is None:
                await redis.set(cache_key_reservations, b'[]', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Записи о бронировании не найдены')
            await redis.set(
                cache_key_reservations,
                orjson.dumps([reservation.model_dump() for reservation in reservations]),
                ex=3600,
            )
            return reservations
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@reservation_router.put(
    '/{reservation_id}',
    response_model=ReservationRead,
    tags=['Reservations'],
    response_class=ORJSONResponse,
)
async def update_reservation_endpoint(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] == 'Сотрудник':
        try:
            reservation = await update_reservation(
                session=session, reservation_id=reservation_id, reservation_data=reservation_data
            )
            if reservation is None:
                return ORJSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND, content='Обновляемая запись о бронировании не найдена'
                )
            cache_key_reservations = get_reservations_cache(restaurant_id=reservation.restaurant_id)
            cache_key_reservation_by_id = get_reservation_by_id_cache(reservation_id=reservation_id)
            cache_key_user_reservations = get_user_reservations_by_id_cache(user_id=reservation.user_id)
            await redis.delete(cache_key_reservations, cache_key_reservation_by_id, cache_key_user_reservations)
            return reservation
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')


@reservation_router.delete(
    '/{reservation_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Reservations'], response_class=ORJSONResponse
)
async def delete_reservation_endpoint(
    reservation_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    if current_user['role'] == 'Сотрудник':
        try:
            reservation = await get_reservation(session=session, reservation_id=reservation_id)
            deleted_reservation = await delete_reservation(session=session, reservation_id=reservation_id)
            if deleted_reservation is False:
                return ORJSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND, content='Удаляемая запись о бронировании не найдена'
                )
            cache_key_reservations = get_reservations_cache(restaurant_id=reservation.restaurant_id)
            cache_key_reservation_by_id = get_reservation_by_id_cache(reservation_id=reservation_id)
            cache_key_user_reservations = get_user_reservations_by_id_cache(user_id=reservation.user_id)
            await redis.delete(cache_key_reservations, cache_key_reservation_by_id, cache_key_user_reservations)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Нет доступа для выполнения этой операции')
