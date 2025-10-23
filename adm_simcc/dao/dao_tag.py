from uuid import UUID, uuid4

import pandas as pd

from adm_simcc.dao import Connection

conn = Connection()


def create_tag(params: dict):
    params["id"] = uuid4()
    SCRIPT_SQL = """
        INSERT INTO public.tags(id, name, color_code)
        VALUES (%(id)s, %(name)s, %(color_code)s);
        """
    return conn.exec(SCRIPT_SQL, params)


# A anotação foi mudada para 'str', pois é o que o router envia
def get_tag(tag_id_str: str = None):
    one = False
    params = {}
    filters = str()

    if tag_id_str:
        one = True
        try:
            # CORREÇÃO 1: Converter a string para UUID
            # CORREÇÃO 2: Usar a chave 'id' no dicionário
            params["id"] = UUID(tag_id_str)
        except ValueError:
            # Lidar com o caso de um ID inválido (opcional, mas bom)
            return {"error": "Invalid Tag ID format"}, 400

        # CORREÇÃO 3: Adicionar espaço antes de "AND"
        filters += " AND id = %(id)s"

    SCRIPT_SQL = f"""
        SELECT id, name, color_code
        FROM public.tags
        WHERE 1 = 1
            {filters}
        """

    result = conn.select(SCRIPT_SQL, params)
    data = pd.DataFrame(result, columns=["id", "name", "color_code"])

    records = data.to_dict(orient="records")

    if one:
        return records[0] if records else {}  # Retorna dict vazio se não achar

    return records


def update_tag(params: dict):
    # Nota: Assumindo que o 'id' (como string) vem no JSON (params)
    # Seria bom convertê-lo para UUID aqui também.
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


# A anotação foi mudada para 'str'
def delete_tag(tag_id_str: str):
    try:
        # CORREÇÃO: Converter a string para UUID
        tag_id_uuid = UUID(tag_id_str)
    except ValueError:
        return {"error": "Invalid Tag ID format"}, 400

    SCRIPT_SQL = """
        DELETE FROM public.tags
        WHERE id = %(id)s;
        """
    # Passa o UUID convertido
    return conn.exec(SCRIPT_SQL, {"id": tag_id_uuid})
