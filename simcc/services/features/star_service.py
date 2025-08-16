from uuid import UUID

from simcc.core.connection import Connection
from simcc.repositories.features import star_repository
from simcc.schemas import user_model
from simcc.schemas.features import star_models


async def post_star(
    conn: Connection, star_data: star_models.CreateStar, user: user_model.User
):
    star = star_models.Star(**star_data.model_dump(), user_id=user.user_id)
    await star_repository.create_star(conn, star)
    return star


async def get_stars(
    conn: Connection, user: user_model.User
) -> list[star_models.Star]:
    star_records = await star_repository.get_stars_by_user_id(
        conn, user_id=user.user_id
    )

    return [star_models.Star(**record) for record in star_records]


async def delete_star(
    conn: Connection, entry_id: UUID, user: user_model.User
) -> bool:
    rows_deleted = await star_repository.delete_star(
        conn, user_id=user.user_id, entry_id=entry_id
    )

    return rows_deleted > 0
