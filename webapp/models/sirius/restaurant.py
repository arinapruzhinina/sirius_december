from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import DEFAULT_SCHEMA, Base


class Restaurant(Base):
    __tablename__ = 'restaurant'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    reservations = relationship('Reservation', back_populates='restaurant', cascade='all, delete-orphan')
    menu = relationship('Dish', back_populates='restaurant', cascade='all, delete-orphan')
