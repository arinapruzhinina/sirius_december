from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.login.router import auth_router
from webapp.crud.user import create_user, get_user
from webapp.db.postgres import get_session
from webapp.schema.login.user import UserCreate, UserLogin, UserLoginResponse, UserRead
from webapp.utils.auth.jwt import jwt_auth


@auth_router.post(
    '/signup',
    response_model=UserRead,
    tags=['Auth'],
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_endpoint(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        user = await create_user(session=session, user_data=user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@auth_router.post('/login', response_model=UserLoginResponse, tags=['Auth'])
async def login(
    body: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    user = await get_user(session=session, user_info=body)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return ORJSONResponse(
        {
            'access_token': jwt_auth.create_token(user_id=user.id, role=user.role),
        }
    )
