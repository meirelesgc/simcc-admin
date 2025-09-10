import httpx
import pandas as pd
from pydantic import UUID4
from zeep import Client

from ..config import settings
from ..dao import Connection
from ..models.researcher import (
    ListResearcherDepartament,
    ListResearchers,
)

PROXY = settings.ALTERNATIVE_CNPQ_SERVICE

adm_database = Connection()
client = Client("http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl")


def researcher_update(researcher):
    SCRIPT_SQL = """
        UPDATE researcher SET
            name = %(name)s,
            lattes_id = %(lattes_id)s,
            institution_id = %(institution_id)s,
            status = %(status)s
        WHERE researcher_id = %(researcher_id)s;
        """
    adm_database.exec(SCRIPT_SQL, researcher)


def cpf_to_lattes(cpf: str):
    cpf = cpf.strip().replace("-", "").replace(".", "")
    if not cpf.isdigit():
        raise ValueError(
            "O CPF deve ser uma string válida contendo apenas números ou formatos com hífen/ponto."
        )
    try:
        if PROXY:
            PROXY_URL = (
                f"https://simcc.uesc.br/v3/api/getIdentificadorCNPq?cpf={cpf}"
            )
            response = httpx.get(PROXY_URL, verify=False, timeout=None).json()
            if response:
                return response
            raise RuntimeError("Identificador não encontrado via proxy.")
        return client.service.getIdentificadorCNPq(
            cpf=cpf, nomeCompleto="", dataNascimento=""
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar o identificador CNPq: {e}")


def validate_lattes(lattes_id):
    try:
        if PROXY:
            PROXY_URL = f"https://simcc.uesc.br/v3/api/getDataAtualizacaoCV?lattes_id={lattes_id}"
            response = httpx.get(PROXY_URL, verify=False, timeout=None).json()
            return bool(response)
        response = client.service.getDataAtualizacaoCV(lattes_id)
        return bool(response)
    except Exception as e:
        print(f"Erro ao validar o Lattes ID: {e}")
        return False


def researcher_insert(ListResearchers: ListResearchers):
    parameters = list()
    # fmt: off
    for researcher in ListResearchers.researcher_list:
        if researcher.cpf:
            researcher.lattes_id = cpf_to_lattes(researcher.cpf)

        if not validate_lattes(researcher.lattes_id):
            raise RuntimeError(f"Erro ao buscar o identificador CNPq: {researcher.lattes_id}")
        parameters.append((
            researcher.researcher_id, researcher.name, researcher.lattes_id,
            researcher.institution_id, researcher.status
        ))

    # fmt: on
    SCRIPT_SQL = """
        INSERT INTO researcher
        (researcher_id, name, lattes_id, institution_id, status)
        VALUES (%s, %s, %s, %s, %s);
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
    researcher_id: str = None,
):
    params = {}
    where_conditions = []

    one = bool(lattes_id or researcher_id)

    if not one:
        where_conditions.append(
            "r.researcher_id NOT IN (SELECT researcher_id FROM graduate_program_student)"
        )

    if institution_id:
        where_conditions.append("r.institution_id = %(institution_id)s")
        params["institution_id"] = str(institution_id)

    if researcher_name:
        where_conditions.append("r.name ILIKE %(researcher_name)s")
        params["researcher_name"] = f"%{researcher_name}%"

    if researcher_id:
        where_conditions.append("r.researcher_id = %(researcher_id)s")
        params["researcher_id"] = researcher_id
    elif lattes_id:
        where_conditions.append("r.lattes_id = %(lattes_id)s")
        params["lattes_id"] = lattes_id

    where_clause = ""
    if where_conditions:
        where_clause = f"WHERE {' AND '.join(where_conditions)}"

    limit_clause = ""
    if rows:
        limit_clause = "LIMIT %(rows)s"
        params["rows"] = rows

    script_sql = f"""
        SELECT DISTINCT
            r.researcher_id,
            r.name,
            r.lattes_id,
            r.institution_id,
            r.created_at,
            r.status,
            r.extra_field
        FROM
            researcher r
        {where_clause}
        ORDER BY
            r.created_at DESC
        {limit_clause};
    """

    registry = adm_database.select(script_sql, params)

    if not registry:
        return {} if one else []

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "researcher_id",
            "name",
            "lattes_id",
            "institution_id",
            "created_at",
            "status",
            "extra_field",
        ],
    ).drop(columns=["created_at"])

    records = data_frame.to_dict(orient="records")

    return records[0] if one and records else records


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
        SELECT researcher_id
        FROM researcher as r
        WHERE similarity(unaccent(LOWER(%s)), unaccent(LOWER(r.name))) > 0.4
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
        SELECT researcher_id
        FROM researcher
        WHERE lattes_id = %s
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
        SELECT dep_id, org_cod, dep_nom, dep_des, dep_email, dep_site, dep_sigla,
            dep_tel
        FROM ufmg.departament dp
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
