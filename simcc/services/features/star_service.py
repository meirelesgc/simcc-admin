from uuid import UUID

from simcc.core.connection import Connection
from simcc.models import user_models
from simcc.models.features import star_models
from simcc.repositories.features import star_repository


async def post_star(
    conn: Connection, star_data: star_models.CreateStar, user: user_models.User
):
    new_star_record = await star_repository.create_star(
        conn, star_data=star_data, user_id=user.id
    )

    return star_models.Star(**new_star_record)


async def get_stars(
    conn: Connection, user: user_models.User
) -> list[star_models.Star]:
    star_records = await star_repository.get_stars_by_user_id(
        conn, user_id=user.id
    )

    return [star_models.Star(**record) for record in star_records]


async def delete_star(
    conn: Connection, entry_id: UUID, user: user_models.User
) -> bool:
    rows_deleted = await star_repository.delete_star(
        conn, user_id=user.id, entry_id=entry_id
    )

    return rows_deleted > 0
