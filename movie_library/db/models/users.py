from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TEXT

from .base import BaseTable


class User(BaseTable):
    __tablename__ = "users"

    username = Column(
        "username",
        TEXT,
        nullable=False,
        unique=True,
        index=True,
        doc="Username for authentication.",
    )
    password = Column(
        "password",
        TEXT,
        nullable=False,
        doc="Hashed password.",
    )
    email = Column(
        "email",
        TEXT,
        nullable=True,
        unique=True,
        index=True,
        doc="Email for notifications.",
    )
