from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from movie_library.db import DeclarativeBase


class UserMovie(DeclarativeBase):
    __tablename__ = 'user_favorite_movies'

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        doc='User id',
    )
    movie_id = Column(
        UUID(as_uuid=True),
        ForeignKey('movies.id', ondelete='CASCADE'),
        primary_key=True,
        doc='Movie id',
    )

    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {', '.join(map(lambda x: f'{x[0]}={x[1]}', columns.items()))}>'
