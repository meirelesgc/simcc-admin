from datetime import datetime
from uuid import UUID, uuid4

import pandas as pd

from adm_simcc.dao import Connection

conn = Connection()


def create_tag(params: dict):
    params["id"] = uuid4()
    params["created_at"] = datetime.utcnow()
    SCRIPT_SQL = """
        INSERT INTO public.tags(id, name, color_code, created_at)
        VALUES (%(id)s, %(name)s, %(color_code)s, %(created_at)s);
        """
    return conn.exec(SCRIPT_SQL, params)


def get_tag(tag_id_str: str = None):
    one = False
    params = {}
    filters = str()

    if tag_id_str:
        one = True
        try:
            params["id"] = UUID(tag_id_str)
        except ValueError:
            return {"error": "Invalid Tag ID format"}, 400

        filters += " AND id = %(id)s"

    SCRIPT_SQL = f"""
        SELECT id, name, color_code, created_at
        FROM public.tags
        WHERE 1 = 1
            {filters}
        """

    result = conn.select(SCRIPT_SQL, params)
    data = pd.DataFrame(
        result, columns=["id", "name", "color_code", "created_at"]
    )

    records = data.to_dict(orient="records")

    if one:
        return records[0] if records else {}

    return records


def update_tag(params: dict):
    try:
        if "id" in params:
            params["id"] = UUID(params["id"])
    except ValueError:
        return {"error": "Invalid Tag ID format for update"}, 400

    SCRIPT_SQL = """
        UPDATE public.tags
        SET name = %(name)s, color_code = %(color_code)s
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, params)


def delete_tag(tag_id_str: str):
    try:
        tag_id_uuid = UUID(tag_id_str)
    except ValueError:
        return {"error": "Invalid Tag ID format"}, 400

    SCRIPT_SQL = """
        DELETE FROM public.tags
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, {"id": tag_id_uuid})
