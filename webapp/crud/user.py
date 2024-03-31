from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.models.sirius.user import User as SQLAUser
from webapp.schema.login.user import UserCreate, UserLogin, UserRead, UserUpdate
from webapp.utils.auth.password import hash_password


async def create_user(session: AsyncSession, user_data: UserCreate) -> UserRead:
    hashed_password = hash_password(user_data.password)
    new_user = SQLAUser(hashed_password=hashed_password, **user_data.model_dump(exclude={'password'}))
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return UserRead.model_validate(new_user)


async def update_user(session: AsyncSession, user_id: int, user_data: UserUpdate) -> UserRead | None:
    result = await session.execute(select(SQLAUser).where(SQLAUser.id == user_id))
    user = result.scalars().first()
    if user:
        if user_data.password:
            hashed_password = hash_password(user_data.password)
            user.hashed_password = hashed_password
        user_data_dict = user_data.model_dump(exclude={'password'})
        for var, value in user_data_dict.items():
            setattr(user, var, value) if value else None
        await session.commit()
        await session.refresh(user)
        return UserRead.model_validate(user)
    return None


async def get_user(session: AsyncSession, user_info: UserLogin) -> SQLAUser | None:
    return (
        await session.scalars(
            select(SQLAUser).where(
                SQLAUser.username == user_info.username,
                SQLAUser.hashed_password == hash_password(user_info.password),
            )
        )
    ).one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserRead | None:
    result = await session.execute(select(SQLAUser).where(SQLAUser.id == user_id))
    user = result.scalars().first()
    if user:
        return UserRead.model_validate(user)
    return None


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(SQLAUser).where(SQLAUser.id == user_id))
    result = result.scalars().first()
    if result:
        await session.delete(result)
        await session.commit()
        return True
    return False
