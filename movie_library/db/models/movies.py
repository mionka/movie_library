from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TEXT

from .base import BaseTable


class Movie(BaseTable):
    __tablename__ = "movies"

    title = Column(
        "title",
        TEXT,
        nullable=False,
        unique=True,
        index=True,
        doc="Title of the movie.",
    )
    description = Column(
        "description",
        TEXT,
        nullable=True,
        doc="Movie description.",
    )
