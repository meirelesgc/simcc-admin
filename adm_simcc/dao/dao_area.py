import datetime
from uuid import UUID, uuid4

import pandas as pd

from adm_simcc.dao import Connection

conn = Connection()


def create_area(params: dict):
    params["id"] = uuid4()
    params["created_at"] = datetime.datetime.now()

    SCRIPT_SQL = """
        INSERT INTO public.areas(id, name, created_at)
        VALUES (%(id)s, %(name)s, %(created_at)s);
        """
    return conn.exec(SCRIPT_SQL, params)


def get_area(area_id_str: str = None):
    one = False
    params = {}
    filters = str()

    if area_id_str:
        one = True
        try:
            params["id"] = UUID(area_id_str)
        except ValueError:
            return {"error": "Invalid area ID format"}, 400

        filters += " AND id = %(id)s"

    SCRIPT_SQL = f"""
        SELECT id, name, created_at
        FROM public.areas
        WHERE 1 = 1
            {filters}
        """

    result = conn.select(SCRIPT_SQL, params)

    data = pd.DataFrame(result, columns=["id", "name", "created_at"])

    records = data.to_dict(orient="records")

    if one:
        return records[0] if records else {}

    return records


def update_area(params: dict):
    try:
        if "id" in params:
            params["id"] = UUID(params["id"])
    except ValueError:
        return {"error": "Invalid area ID format for update"}, 400

    SCRIPT_SQL = """
        UPDATE public.areas
        SET name = %(name)s
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, params)


def delete_area(area_id_str: str):
    try:
        area_id_uuid = UUID(area_id_str)
    except ValueError:
        return {"error": "Invalid area ID format"}, 400

    SCRIPT_SQL = """
        DELETE FROM public.areas
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, {"id": area_id_uuid})
