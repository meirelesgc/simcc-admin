import pandas as pd
from pydantic import UUID4
from zeep import Client

from ..dao import Connection
from ..models.researcher import (
    ListResearcherDepartament,
    ListResearchers,
)

adm_database = Connection()
# simcc_database = Connection(database=os.environ["SIMCC_DATABASE"])
CNPq = Client("http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl")


def researcher_insert(ListResearchers: ListResearchers):
    parameters = list()
    # fmt: off
    for researcher in ListResearchers.researcher_list:
        parameters.append((
            researcher.researcher_id, researcher.name, researcher.lattes_id,
            researcher.institution_id
        ))
    # fmt: on

    SCRIPT_SQL = """
        INSERT INTO researcher
        (researcher_id, name, lattes_id, institution_id)
        VALUES (%s, %s, %s, %s);
        """
    adm_database.execmany(SCRIPT_SQL, parameters)


def researcher_delete(researcher_id: UUID4):
    parameters = [researcher_id, researcher_id, researcher_id, researcher_id]
    SCRIPT_SQL = """
        DELETE FROM ufmg.researcher
        WHERE researcher_id = %s;

        DELETE FROM graduate_program_researcher
        WHERE researcher_id = %s;

        DELETE FROM graduate_program_student
        WHERE researcher_id = %s;

        DELETE FROM researcher
        WHERE researcher_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def researcher_basic_query(
    institution_id: UUID4 = None,
    researcher_name: str = None,
    rows: int = None,
    lattes_id: str = None,
):
    parameters = list()
    filter_name = filter_limit = filter_institution = filter_lattes_id = str()

    if institution_id:
        filter_institution = """
            AND r.institution_id = %s
            """
        parameters += [institution_id]

    if researcher_name:
        filter_name = """
            AND name ILIKE %s
            """
        parameters += [researcher_name]
    if rows:
        filter_limit = "LIMIT %s"
        parameters += [rows]

    if lattes_id:
        filter_lattes_id = "AND lattes_id = %s"
        parameters += [lattes_id]

    SCRIPT_SQL = f"""
        SELECT DISTINCT
            r.researcher_id,
            r.name,
            r.lattes_id,
            r.institution_id,
            r.created_at
        FROM
            researcher r
        WHERE
            r.researcher_id NOT IN
            (SELECT researcher_id FROM graduate_program_student)
            {filter_institution}
            {filter_name}
            {filter_lattes_id}
        GROUP BY
            r.researcher_id,
            r.name,
            r.lattes_id,
            r.institution_id,
            r.created_at
        ORDER BY
            r.created_at DESC
            {filter_limit};
        """
    registry = adm_database.select(SCRIPT_SQL, parameters)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "researcher_id",
            "name",
            "lattes_id",
            "institution_id",
            "created_at",
        ],
    )
    SCRIPT_SQL = """
        SELECT
            r.lattes_id,
            r.last_update
        FROM
            researcher r
        """

    data_frame = data_frame.drop(columns=["created_at"])
    return data_frame.fillna("Não esta atualizado").to_dict(orient="records")


def researcher_count(institution_id: UUID4 = None):
    parameters = list()
    filter_institution = str()
    if institution_id:
        filter_institution = "WHERE institution_id = %s"
        parameters.extend([institution_id])

    SCRIPT_SQL = f"SELECT COUNT(*) FROM researcher {filter_institution}"

    registry = adm_database.select(SCRIPT_SQL, parameters)

    # psycopg2 retorna uma lista de truplas,
    # quero apenas o primeiro valor da primeira lista
    return registry[0][0]


def researcher_query_name(researcher_name: str):
    parameters = [researcher_name]
    SCRIPT_SQL = """
    SELECT
        researcher_id
    FROM
        researcher as r
    WHERE
        similarity(unaccent(LOWER(%s)), unaccent(LOWER(r.name))) > 0.4
    LIMIT 1;
    """

    registry = adm_database.select(SCRIPT_SQL, parameters)

    if registry:
        return registry[0][0]
    else:
        return str()


def researcher_search_id(lattes_id):
    parameters = [lattes_id]
    SCRIPT_SQL = """
        SELECT
            researcher_id
        FROM
            researcher
        WHERE
            lattes_id = %s
        """
    researcher_id = adm_database.select(SCRIPT_SQL, parameters)

    if researcher_id:
        return researcher_id[0][0]
    else:
        return str()


def researcher_departament_insert(
    ListResearcherDepartament: ListResearcherDepartament,
):
    parameters = list()

    for researcher in ListResearcherDepartament.researcher_departament:
        parameters.append((researcher.dep_id, researcher.researcher_id))

    SCRIPT_SQL = """
        INSERT INTO ufmg.departament_researcher (dep_id, researcher_id)
        VALUES (%s, %s);
        """
    adm_database.execmany(SCRIPT_SQL, parameters)


def researcher_departament_basic_query(researcher_id):
    SCRIPT_SQL = """
        SELECT
            dep_id, org_cod, dep_nom, dep_des, dep_email, dep_site, dep_sigla, 
            dep_tel
        FROM
            ufmg.departament dp
            LEFT JOIN ufmg.departament_researcher dpr ON dpr.dep_id = dp.dep_id
        WHERE
            dpr.researcher_id = %s;
        """

    registry = adm_database.select(SCRIPT_SQL, researcher_id)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "dep_id",
            "org_cod",
            "dep_nom",
            "dep_des",
            "dep_email",
            "dep_site",
            "dep_sigla",
            "dep_tel",
        ],
    )

    return data_frame.to_dict(orient="records")


def researcher_departament_delete(researcher):
    SCRIPT_SQL = """
        DELETE FROM ufmg.departament_researcher
        WHERE researcher_id = (SELECT researcher_id FROM researcher WHERE lattes_id = %s) 
        AND dep_id = %s;
        """
    adm_database.exec(
        SCRIPT_SQL, [researcher[0]["lattes_id"], researcher[0]["dep_id"]]
    )
