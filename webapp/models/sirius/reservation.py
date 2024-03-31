from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import DEFAULT_SCHEMA, Base


class Reservation(Base):
    __tablename__ = 'reservation'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{DEFAULT_SCHEMA}.user.id'))
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{DEFAULT_SCHEMA}.restaurant.id'))
    date_reserv: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    guest_count: Mapped[int] = mapped_column(Integer)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[str] = mapped_column(String)

    user = relationship('User', back_populates='reservations')
    restaurant = relationship('Restaurant', back_populates='reservations')
