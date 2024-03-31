import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import DEFAULT_SCHEMA, Base

if TYPE_CHECKING:
    from webapp.models.sirius.file import File


class RoleCategory(str, enum.Enum):
    ADMIN = 'Администратор'
    STAFF = 'Сотрудник'
    USER = 'Пользователь'


RoleCategoryType: ENUM = ENUM(
    RoleCategory,
    name='role_category',
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = ({'schema': DEFAULT_SCHEMA},)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    role: Mapped[ENUM] = mapped_column(RoleCategoryType, default='USER')
    files: Mapped[List['File']] = relationship(
        'File',
        secondary=f'{DEFAULT_SCHEMA}.user_file',
        back_populates='users',
    )

    reservations = relationship('Reservation', back_populates='user', cascade='all, delete-orphan')
