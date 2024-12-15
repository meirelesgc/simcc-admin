import pandas as pd
from pydantic import UUID4

from ..dao import Connection
from ..models.institution import Institution, ListInstitutions

adm_database = Connection()


def institution_insert(ListInstitutions: ListInstitutions):
    values_str = str()
    for institution in ListInstitutions.institution_list:
        values_str += f"""('{institution.institution_id}', '{institution.name}', '{institution.acronym}', '{institution.lattes_id}'),"""

    # Criação do script de insert.
    # Unifiquei em um unico comando para facilitar
    # o retorno da mensagem de erro
    SCRIPT_SQL = f"""
        INSERT INTO public.institution
        (institution_id, name, acronym, lattes_id)
        VALUES {values_str[:-1]};
        """

    adm_database.exec(SCRIPT_SQL)


def institution_full_query(institution_id: UUID4 = None):
    filter_institution = str()
    if institution_id:
        filter_institution = f"WHERE i.institution_id = '{institution_id}'"

    SCRIPT_SQL = f"""
        SELECT
            i.name AS name,
            i.institution_id,
            r.count_r,
            gp.count_gp,
            gpr.count_gpr,
            gps.count_gps,
            d.count_d,
            (SELECT COUNT(*) FROM ufmg.technician) as count_t
        FROM
            institution i
            LEFT JOIN (SELECT institution_id, COUNT(DISTINCT researcher_id) AS count_r FROM researcher GROUP BY institution_id) r
            ON r.institution_id = i.institution_id
            LEFT JOIN (SELECT institution_id, COUNT(DISTINCT graduate_program_id) AS count_gp FROM graduate_program GROUP BY institution_id) gp
            ON gp.institution_id = i.institution_id
            LEFT JOIN (SELECT gp.institution_id, SUM(gpr.count_r) AS count_gpr
                    FROM graduate_program gp
                    LEFT JOIN (SELECT graduate_program_id, COUNT(DISTINCT researcher_id) AS count_r FROM graduate_program_researcher GROUP BY graduate_program_id) gpr
                    ON gpr.graduate_program_id = gp.graduate_program_id GROUP BY institution_id) gpr
            ON gpr.institution_id = i.institution_id
            LEFT JOIN (SELECT gp.institution_id, SUM(gps.count_s) AS count_gps
                    FROM graduate_program gp
                    LEFT JOIN (SELECT graduate_program_id, COUNT(DISTINCT researcher_id) AS count_s FROM graduate_program_student GROUP BY graduate_program_id) gps
                    ON gps.graduate_program_id = gp.graduate_program_id GROUP BY institution_id) gps
            ON gps.institution_id = i.institution_id
            LEFT JOIN (SELECT institution_id, COUNT(ur.researcher_id) AS count_d
                    FROM ufmg.researcher ur
                    LEFT JOIN researcher r ON r.researcher_id = ur.researcher_id
                    GROUP BY r.institution_id) d
                    ON d.institution_id = i.institution_id
        {filter_institution}
        GROUP BY
            i.institution_id,
            i.name,
            r.count_r,
            gp.count_gp,
            gpr.count_gpr,
            gps.count_gps,
            d.count_d;
        """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "name",
            "institution_id",
            "count_r",
            "count_gp",
            "count_gpr",
            "count_gps",
            "count_d",
            "count_t",
        ],
    )

    return data_frame.fillna(0).to_dict(orient="records")


def institution_basic_query(institution_id: UUID4):
    SCRIPT_SQL = f"""
        SELECT
            institution_id,
            name,
            acronym,
            lattes_id
            FROM
            institution
        WHERE
            institution_id = '{institution_id}'
        """

    registry = adm_database.select(SCRIPT_SQL=SCRIPT_SQL)

    data_frame = pd.DataFrame(
        registry, columns=["institution_id", "name", "acronym", "lattes_id"]
    )

    # to_dict retorna uma lista, e eu so quero o primeiro valor
    return data_frame.to_dict(orient="records")[0]


def institution_query_name(institution_name: str):
    SCRIPT_SQL = f"""
    SELECT
        institution_id
    FROM
        institution as i
    WHERE
        similarity(unaccent(LOWER('{institution_name.replace("'", "''")}')), unaccent(LOWER(i.name))) > 0.4
    LIMIT 1;
    """

    registry = adm_database.select(SCRIPT_SQL)

    if registry:
        return registry[0][0]
    else:
        return None


def delete_institution(institution_id):
    SCRIPT_SQL = """
        DELETE FROM institution WHERE institution_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [institution_id])


def update_institution(institution: Institution):
    SCRIPT_SQL = """
        UPDATE institution SET
            name = %(name)s,
            acronym = %(acronym)s,
            lattes_id = %(lattes_id)s
        WHERE institution_id = %(institution_id)s;
        """
    adm_database.exec(SCRIPT_SQL, institution.model_dump())
