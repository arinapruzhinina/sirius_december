import orjson
from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.login.router import user_router
from webapp.cache.key_builder import get_user_by_id_cache, get_user_reservations_by_id_cache
from webapp.crud.reservation import get_reservations_for_user
from webapp.crud.user import delete_user, get_user_by_id, update_user
from webapp.db.postgres import get_session
from webapp.db.redis import get_redis
from webapp.schema.login.user import UserRead, UserUpdate
from webapp.schema.reservation.reservation import ReservationRead
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@user_router.get('/me', response_model=UserRead, tags=['Users'], response_class=ORJSONResponse)
async def get_me_endpoint(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    try:
        cache_key_user = get_user_by_id_cache(user_id=current_user['user_id'])
        cached_user = await redis.get(cache_key_user)
        if cached_user:
            if cached_user == b'{}':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Пользователь не найден')
            return orjson.loads(cached_user)
        else:
            user = await get_user_by_id(session=session, user_id=current_user['user_id'])
            if user is None:
                await redis.set(cache_key_user, b'{}', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Пользователь не найден')
            await redis.set(cache_key_user, orjson.dumps(user.model_dump()), ex=3600)
            return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.get(
    '/me/reservations', response_model=list[ReservationRead], tags=['Users'], response_class=ORJSONResponse
)
async def get_user_reservations(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    try:
        cache_key_user_reservations = get_user_reservations_by_id_cache(user_id=current_user['user_id'])
        cached_user_reservations = await redis.get(cache_key_user_reservations)
        if cached_user_reservations:
            if cached_user_reservations == b'[]':
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Бронирований не найдено')
            return orjson.loads(cached_user_reservations)
        else:
            user_reservations = await get_reservations_for_user(session=session, user_id=current_user['user_id'])
            if user_reservations is None:
                await redis.set(cache_key_user_reservations, b'[]', ex=3600)
                return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Бронирований не найдено')
            await redis.set(
                cache_key_user_reservations,
                orjson.dumps([user_reservation.model_dump() for user_reservation in user_reservations]),
                ex=3600,
            )
            return user_reservations
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.put('/me/update', response_model=UserRead, tags=['Users'], response_class=ORJSONResponse)
async def update_user_endpoint(
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    try:
        user = await update_user(session=session, user_id=current_user['user_id'], user_data=user_data)
        if user is None:
            return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Пользователь не найден')
        cache_key_user = get_user_by_id_cache(user_id=current_user['user_id'])
        await redis.delete(cache_key_user)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_router.delete('/me/delete', status_code=status.HTTP_204_NO_CONTENT, tags=['Users'], response_class=ORJSONResponse)
async def delete_user_endpoint(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    current_user: JwtTokenT = Depends(jwt_auth.get_current_user),
):
    try:
        success = await delete_user(session=session, user_id=current_user['user_id'])
        if success is False:
            return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Пользователь не найден')
        cache_key_user = get_user_by_id_cache(user_id=current_user['user_id'])
        cache_key_user_reservations = get_user_reservations_by_id_cache(user_id=current_user['user_id'])
        await redis.delete(cache_key_user, cache_key_user_reservations)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
