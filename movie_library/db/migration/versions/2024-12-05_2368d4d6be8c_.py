"""empty message

Revision ID: 2368d4d6be8c
Revises: 
Create Date: 2024-12-05 00:40:47.536825

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "2368d4d6be8c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "movies",
        sa.Column("title", sa.TEXT(), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "dt_created",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "dt_updated",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__movies")),
        sa.UniqueConstraint("id", name=op.f("uq__movies__id")),
    )
    op.create_index(op.f("ix__movies__title"), "movies", ["title"], unique=True)
    op.create_table(
        "users",
        sa.Column("username", sa.TEXT(), nullable=False),
        sa.Column("password", sa.TEXT(), nullable=False),
        sa.Column("email", sa.TEXT(), nullable=True),
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "dt_created",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "dt_updated",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__users")),
        sa.UniqueConstraint("id", name=op.f("uq__users__id")),
    )
    op.create_index(op.f("ix__users__email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix__users__username"), "users", ["username"], unique=True)
    op.create_table(
        "user_favorite_movies",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("movie_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["movie_id"], ["movies.id"], name=op.f("fk__user_favorite_movies__movie_id__movies"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk__user_favorite_movies__user_id__users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "movie_id", name=op.f("pk__user_favorite_movies")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_favorite_movies")
    op.drop_index(op.f("ix__users__username"), table_name="users")
    op.drop_index(op.f("ix__users__email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix__movies__title"), table_name="movies")
    op.drop_table("movies")
    # ### end Alembic commands ###