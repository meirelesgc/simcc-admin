from uuid import UUID, uuid4

import pandas as pd

from adm_simcc.dao import Connection

conn = Connection()


def create_tag(params: dict):
    params["id"] = uuid4()
    SCRIPT_SQL = """
        INSERT INTO public.tags(id, name)
        VALUES (%(id)s, %(name)s);
        """
    return conn.exec(SCRIPT_SQL, params)


def get_tag(tag_id: UUID = None):
    one = False
    params = {}
    filters = str()

    if tag_id:
        one = True
        params["tag_id"] = tag_id
        filters += "AND id = %(id)s"

    SCRIPT_SQL = f"""
        SELECT id, name
        FROM public.tags
        WHERE 1 = 1
            {filters}
        """

    result = conn.select(SCRIPT_SQL, params)
    data = pd.DataFrame(result, columns=["id", "name"])

    records = data.to_dict(orient="records")
    return records[0] if one else records


def update_tag(params: dict):
    SCRIPT_SQL = """
        UPDATE public.tags
        SET name = %(name)s
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, params)


def delete_tag(tag_id: UUID):
    SCRIPT_SQL = """
        DELETE FROM public.tags
        WHERE id = %(id)s;
        """
    return conn.exec(SCRIPT_SQL, {"id": tag_id})
