from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.models.sirius.reservation import Reservation
from webapp.schema.reservation.reservation import ReservationCreate, ReservationRead, ReservationUpdate


async def create_reservation(session: AsyncSession, reservation_data: ReservationCreate) -> ReservationRead | None:
    reservation = Reservation(**reservation_data.model_dump())
    session.add(reservation)
    await session.commit()
    await session.refresh(reservation)
    return ReservationRead.model_validate(reservation)


async def get_reservation(session: AsyncSession, reservation_id: int) -> ReservationRead | None:
    statement = select(Reservation).where(Reservation.id == reservation_id)
    result = await session.execute(statement)
    reservation = result.scalar()
    if not reservation:
        return None

    return ReservationRead.model_validate(reservation)


async def get_reservations(session: AsyncSession, restaurant_id: int) -> list[ReservationRead] | None:
    statement = select(Reservation).where(Reservation.id == restaurant_id)
    result = await session.execute(statement)
    reservations = result.scalars().all()
    if not reservations:
        return None

    return [ReservationRead.model_validate(reservation) for reservation in reservations]


async def update_reservation(
    session: AsyncSession, reservation_id: int, reservation_data: ReservationUpdate
) -> ReservationRead | None:
    statement = select(Reservation).where(Reservation.id == reservation_id)
    result = await session.execute(statement)
    reservation = result.scalar()
    if not reservation:
        return None

    for field, value in reservation_data.model_dump(exclude_unset=True).items():
        setattr(reservation, field, value)

    await session.commit()
    await session.refresh(reservation)
    return ReservationRead.model_validate(reservation)


async def delete_reservation(session: AsyncSession, reservation_id: int) -> bool:
    statement = select(Reservation).where(Reservation.id == reservation_id)
    result = await session.execute(statement)
    reservation = result.scalar()
    if not reservation:
        return False

    await session.delete(reservation)
    await session.commit()
    return True


async def get_reservations_for_user(session: AsyncSession, user_id: int) -> list[ReservationRead] | None:
    statement = select(Reservation).where(Reservation.user_id == user_id)
    result = await session.execute(statement)
    reservations = result.scalars().all()
    if not reservations:
        return None

    return [ReservationRead.model_validate(reservation) for reservation in reservations]
