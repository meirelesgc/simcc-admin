from uuid import UUID

import pandas as pd

from ..dao import Connection

adm_database = Connection()


def gpr_insert(gpr):
    SCRIPT_SQL = """
        INSERT INTO graduate_program_researcher(
            graduate_program_id, researcher_id, year, type_)
        VALUES (%(graduate_program_id)s, %(researcher_id)s,
            %(year)s, %(type_)s);
        """
    return adm_database.execmany(SCRIPT_SQL, gpr)


def graduate_program_researcher_insert_lattes(gpr):
    SCRIPT_SQL = """
        INSERT INTO graduate_program_researcher(
            graduate_program_id, researcher_id, year, type_)
        SELECT %(graduate_program_id)s, researcher_id, %(year)s, %(type_)s
        FROM researcher
        WHERE lattes_id = %(lattes_id)s;
        """
    adm_database.execmany(SCRIPT_SQL, gpr)


def gpr_delete(gpr):
    SCRIPT_SQL = """
        DELETE FROM graduate_program_researcher
        WHERE researcher_id = %(lattes_id)s
        AND graduate_program_id = %(graduate_program_id)s;
    """
    return adm_database.exec(SCRIPT_SQL, gpr[0])


def graduate_program_researcher_count(
    institution_id: UUID = None, graduate_program_id: UUID = None
):
    parameters = list()

    filter_institution = str()
    if institution_id:
        filter_institution = """
            WHERE graduate_program_id IN (
                    SELECT graduate_program_id
                    FROM graduate_program
                    WHERE institution_id = %s)"""
        parameters.append(institution_id)

    filter_graduate_program = str()
    if graduate_program_id:
        filter_graduate_program = """
            WHERE graduate_program_id = %s"""
        parameters.append(graduate_program_id)

    SCRIPT_SQL = f"""
        SELECT COUNT(*)
        FROM graduate_program_researcher
        {filter_institution}
        {filter_graduate_program}
        GROUP BY graduate_program_id;
        """

    registry = adm_database.select(SCRIPT_SQL, parameters)
    return registry[0][0]


def graduate_program_researcher_basic_query(
    graduate_program_id: UUID, type_: str = None
):
    parameters = []
    filter_program = str()

    if graduate_program_id:
        parameters.append(graduate_program_id)
        filter_program = "AND gpr.graduate_program_id = %s"

    type_filter = str()
    if type_:
        type_filter = "AND type_ = %s"
        parameters.append(type_)

    SCRIPT_SQL = f"""
        WITH gpr_cte AS (
            SELECT researcher_id, json_agg(row_to_json(gpr)) AS gpr_json
            FROM graduate_program_researcher gpr
            WHERE 1 = 1
                {filter_program}
                {type_filter}
            GROUP BY researcher_id)
        SELECT r.researcher_id, r.name, r.lattes_id, gpr_cte.gpr_json
            AS participation
        FROM researcher r
        INNER JOIN gpr_cte
            ON r.researcher_id = gpr_cte.researcher_id
        ORDER BY r.name
        """

    registry = adm_database.select(SCRIPT_SQL, parameters)

    data_frame = pd.DataFrame(
        registry,
        columns=["researcher_id", "name", "lattes_id", "participation"],
    )

    return data_frame.to_dict(orient="records")
