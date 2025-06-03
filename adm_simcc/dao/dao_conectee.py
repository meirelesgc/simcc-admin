import re
import unicodedata
from typing import Optional
from uuid import UUID, uuid4

import pandas as pd
import psycopg2
from numpy import nan

from ..dao import Connection
from ..models.departament import ListDiscipline
from ..models.teachers import ListRole
from ..models.technician import ListTechnicianDepartament

adm_database = Connection()


def departament_basic_query(
    dep_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
):
    parameters = {}
    filter_departament_id = ""
    if dep_id:
        filter_departament_id = "AND d.dep_id = %(dep_id)s"
        parameters["dep_id"] = dep_id

    join_menager = ""
    filter_menager = ""
    if user_id:
        join_menager = "INNER JOIN users u ON u.email = ANY(d.menagers)"
        filter_menager = "AND u.user_id = %(user_id)s"
        parameters["user_id"] = user_id

    SCRIPT_SQL = f"""
        SELECT
            d.dep_id, d.org_cod, d.dep_nom, d.dep_des, d.dep_email, d.dep_site,
            d.dep_sigla, d.dep_tel, d.img_data, d.menagers, -- Adicione 'd.menagers' aqui
            d.created_at, d.updated_at -- Supondo que essas colunas existam
        FROM
            UFMG.departament d
        {join_menager} 
        WHERE 1 = 1
            {filter_departament_id}
            {filter_menager}
    """

    registry = adm_database.select(SCRIPT_SQL, parameters)

    columns = [
        "dep_id",
        "org_cod",
        "dep_nom",
        "dep_des",
        "dep_email",
        "dep_site",
        "dep_sigla",
        "dep_tel",
        "img_data",
        "menagers",
        "created_at",
        "updated_at",
    ]
    data_frame = pd.DataFrame(registry, columns=columns)

    return data_frame.to_dict(orient="records")


def delete_ufmg_researcher(id):
    delete_filter = "WHERE researcher_id = %(id)s" if id else str()

    SCRIPT_SQL = f"""
        DELETE FROM ufmg.researcher
        {delete_filter}
        """
    adm_database.exec(SCRIPT_SQL, {"id": id})


def delete_ufmg_technician(id):
    delete_filter = "WHERE technician_id = %(id)s" if id else str()

    SCRIPT_SQL = f"""
        DELETE FROM ufmg.technician
        {delete_filter}
        """
    adm_database.exec(SCRIPT_SQL, {"id": id})


def normalize_technicians(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "matric": "registration_number",
        "insufmg": "ufmg_registration_number",
        "nome": "full_name",
        "genero": "gender",
        "denosit": "employment_status_description",
        "rt": "work_regime",
        "classe": "job_class",
        "cargo": "job_title",
        "nivel": "job_rank",
        "ref": "job_reference_code",
        "titulacao": "academic_degree",
        "setor": "department_name",
        "detalhesetor": "function_location",
        "dtingorg": "organization_entry_date",
        "dataprog": "last_promotion_date",
        "year_charge": "year_charge",
        "semester": "semester_reference",
        "sexo": "gender",
        "sit": "status_code",
        "clas": "job_class",
        "denocarg": "job_title",
        "denoclasse": "job_rank",
        "denotit": "academic_degree",
        "denosetor": "department_name",
        "cat": "career_category",
        "unid": "academic_unit",
        "grexc": "unit_code",
        "fun": "function_code",
        "funniv": "position_code",
        "dtchefinic": "leadership_start_date",
        "dtcheffim": "leadership_end_date",
        "nomefunc": "current_function_name",
        "exercfunc": "function_location",
        "ins_ufmg": "ufmg_registration_number",
    }
    df = df.copy()
    df.rename(
        columns={k: v for k, v in mapping.items() if k in df.columns},
        inplace=True,
    )
    if "job_class" in df.columns:
        df["job_class"] = pd.to_numeric(df["job_class"], errors="coerce")
    for col in [
        "organization_entry_date",
        "last_promotion_date",
        "leadership_start_date",
        "leadership_end_date",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], errors="coerce", dayfirst=True
            ).dt.date
    return df


def get_technician_id(full_name):
    SCRIPT_SQL = """
        SELECT technician_id
        FROM ufmg.technician
        WHERE full_name ILIKE %(full_name)s
        """
    result = adm_database.select(SCRIPT_SQL, {"full_name": full_name})
    if result:
        return result[0][0]


def post_ufmg_technician(technician):
    technician = pd.DataFrame(technician)
    technician = normalize(technician)
    technician = normalize_technicians(technician)
    technician["technician_id"] = technician["full_name"].apply(
        get_technician_id
    )
    expected_columns = [
        "technician_id",
        "full_name",
        "gender",
        "status_code",
        "work_regime",
        "job_class",
        "job_title",
        "job_rank",
        "job_reference_code",
        "academic_degree",
        "organization_entry_date",
        "last_promotion_date",
        "employment_status_description",
        "department_name",
        "career_category",
        "academic_unit",
        "unit_code",
        "function_code",
        "position_code",
        "leadership_start_date",
        "leadership_end_date",
        "current_function_name",
        "function_location",
        "registration_number",
        "ufmg_registration_number",
        "semester_reference",
    ]
    for col in expected_columns:
        if col not in technician.columns:
            technician[col] = None
    technician = technician.replace(nan, None)
    technician = technician.replace({pd.NaT: None})

    not_found = technician[technician["technician_id"].isna()]
    technician = technician.dropna(subset=["technician_id"])

    not_found["technician_id"] = [str(uuid4()) for _ in range(len(not_found))]

    SCRIPT_SQL = """
        INSERT INTO ufmg.technician(technician_id, full_name, gender,
            status_code, work_regime, job_class, job_title, job_rank,
            job_reference_code, academic_degree, organization_entry_date,
            last_promotion_date, employment_status_description, department_name,
            career_category, academic_unit, unit_code, function_code,
            position_code, leadership_start_date, leadership_end_date,
            current_function_name, function_location, registration_number,
            ufmg_registration_number, semester_reference)
        VALUES (%(technician_id)s, %(full_name)s, %(gender)s,
            %(status_code)s, %(work_regime)s, %(job_class)s, %(job_title)s,
            %(job_rank)s, %(job_reference_code)s, %(academic_degree)s,
            %(organization_entry_date)s, %(last_promotion_date)s,
            %(employment_status_description)s, %(department_name)s,
            %(career_category)s, %(academic_unit)s, %(unit_code)s,
            %(function_code)s, %(position_code)s, %(leadership_start_date)s,
            %(leadership_end_date)s, %(current_function_name)s,
            %(function_location)s, %(registration_number)s,
            %(ufmg_registration_number)s, %(semester_reference)s)
        ON CONFLICT (technician_id) DO UPDATE
        SET
            full_name                       = EXCLUDED.full_name,
            gender                          = EXCLUDED.gender,
            status_code                     = EXCLUDED.status_code,
            work_regime                     = EXCLUDED.work_regime,
            job_class                       = EXCLUDED.job_class,
            job_title                       = EXCLUDED.job_title,
            job_rank                        = EXCLUDED.job_rank,
            job_reference_code              = EXCLUDED.job_reference_code,
            academic_degree                 = EXCLUDED.academic_degree,
            organization_entry_date         = EXCLUDED.organization_entry_date,
            last_promotion_date             = EXCLUDED.last_promotion_date,
            employment_status_description   = EXCLUDED.employment_status_description,
            department_name                 = EXCLUDED.department_name,
            career_category                 = EXCLUDED.career_category,
            academic_unit                   = EXCLUDED.academic_unit,
            unit_code                       = EXCLUDED.unit_code,
            function_code                   = EXCLUDED.function_code,
            position_code                   = EXCLUDED.position_code,
            leadership_start_date           = EXCLUDED.leadership_start_date,
            leadership_end_date             = EXCLUDED.leadership_end_date,
            current_function_name           = EXCLUDED.current_function_name,
            function_location               = EXCLUDED.function_location,
            registration_number             = EXCLUDED.registration_number,
            ufmg_registration_number        = EXCLUDED.ufmg_registration_number,
            semester_reference              = EXCLUDED.semester_reference;
    """  # noqa: E501

    adm_database.execmany(SCRIPT_SQL, technician.to_dict(orient="records"))
    adm_database.execmany(SCRIPT_SQL, not_found.to_dict(orient="records"))
    return {
        "update": technician.to_dict(orient="records"),
        "insert": not_found.to_dict(orient="records"),
    }


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    def norm(texto):
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("utf-8")
        texto = texto.lower()
        texto = re.sub(r"\s+", "_", texto)
        texto = re.sub(r"[^a-z0-9_]", "", texto)
        return texto

    df.columns = [norm(col) for col in df.columns]
    return df


def normalize_researchers(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "nome": "full_name",
        "genero": "gender",
        "sit": "status_code",
        "rt": "work_regime",
        "clas": "job_class",
        "denocarg": "job_title",
        "denoclasse": "job_rank",
        "ref": "job_reference_code",
        "denotit": "academic_degree",
        "dtingorg": "organization_entry_date",
        "dataprog": "last_promotion_date",
        "denosit": "employment_status_description",
        "denosetor": "department_name",
        "cat": "career_category",
        "unid": "academic_unit",
        "grexc": "unit_code",
        "fun": "function_code",
        "funniv": "position_code",
        "dtchefinic": "leadership_start_date",
        "dtcheffim": "leadership_end_date",
        "nomefunc": "current_function_name",
        "exercfunc": "function_location",
        "matric": "registration_number",
        "inscufmg": "ufmg_registration_number",
        "semester": "semester_reference",
    }
    df = df.copy()
    df.rename(
        columns={k: v for k, v in mapping.items() if k in df.columns},
        inplace=True,
    )
    if "job_class" in df.columns:
        df["job_class"] = pd.to_numeric(df["job_class"], errors="coerce")
    for col in [
        "organization_entry_date",
        "last_promotion_date",
        "leadership_start_date",
        "leadership_end_date",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], errors="coerce", dayfirst=True
            ).dt.date
    return df


def get_researcher_id(name):
    SCRIPT_SQL = """
        SELECT researcher_id
        FROM researcher
        WHERE name ILIKE %(name)s
        """
    result = adm_database.select(SCRIPT_SQL, {"name": name})
    if result:
        return result[0][0]


def post_ufmg_researcher(researcher):
    researcher = pd.DataFrame(researcher)
    researcher = normalize(researcher)
    researcher = normalize_researchers(researcher)
    researcher["researcher_id"] = researcher["full_name"].apply(
        get_researcher_id
    )

    expected_columns = [
        "researcher_id",
        "full_name",
        "gender",
        "status_code",
        "work_regime",
        "job_class",
        "job_title",
        "job_rank",
        "job_reference_code",
        "academic_degree",
        "organization_entry_date",
        "last_promotion_date",
        "employment_status_description",
        "department_name",
        "career_category",
        "academic_unit",
        "unit_code",
        "function_code",
        "position_code",
        "leadership_start_date",
        "leadership_end_date",
        "current_function_name",
        "function_location",
        "registration_number",
        "ufmg_registration_number",
        "semester_reference",
    ]

    for col in expected_columns:
        if col not in researcher.columns:
            researcher[col] = None

    researcher = researcher.replace(nan, None)
    researcher = researcher.replace({pd.NaT: None})

    not_found = researcher[researcher["researcher_id"].isna()]
    researcher = researcher.dropna(subset=["researcher_id"])

    SCRIPT_SQL = """
        INSERT INTO ufmg.researcher(researcher_id, full_name, gender,
            status_code, work_regime, job_class, job_title, job_rank,
            job_reference_code, academic_degree, organization_entry_date,
            last_promotion_date, employment_status_description, department_name,
            career_category, academic_unit, unit_code, function_code,
            position_code, leadership_start_date, leadership_end_date,
            current_function_name, function_location, registration_number,
            ufmg_registration_number, semester_reference)
        VALUES (%(researcher_id)s, %(full_name)s, %(gender)s,
            %(status_code)s, %(work_regime)s, %(job_class)s, %(job_title)s,
            %(job_rank)s, %(job_reference_code)s, %(academic_degree)s,
            %(organization_entry_date)s, %(last_promotion_date)s,
            %(employment_status_description)s, %(department_name)s,
            %(career_category)s, %(academic_unit)s, %(unit_code)s,
            %(function_code)s, %(position_code)s, %(leadership_start_date)s,
            %(leadership_end_date)s, %(current_function_name)s,
            %(function_location)s, %(registration_number)s,
            %(ufmg_registration_number)s, %(semester_reference)s)
        ON CONFLICT (researcher_id) DO UPDATE
        SET
            full_name                       = EXCLUDED.full_name,
            gender                          = EXCLUDED.gender,
            status_code                     = EXCLUDED.status_code,
            work_regime                     = EXCLUDED.work_regime,
            job_class                       = EXCLUDED.job_class,
            job_title                       = EXCLUDED.job_title,
            job_rank                        = EXCLUDED.job_rank,
            job_reference_code              = EXCLUDED.job_reference_code,
            academic_degree                 = EXCLUDED.academic_degree,
            organization_entry_date         = EXCLUDED.organization_entry_date,
            last_promotion_date             = EXCLUDED.last_promotion_date,
            employment_status_description   = EXCLUDED.employment_status_description,
            department_name                 = EXCLUDED.department_name,
            career_category                 = EXCLUDED.career_category,
            academic_unit                   = EXCLUDED.academic_unit,
            unit_code                       = EXCLUDED.unit_code,
            function_code                   = EXCLUDED.function_code,
            position_code                   = EXCLUDED.position_code,
            leadership_start_date           = EXCLUDED.leadership_start_date,
            leadership_end_date             = EXCLUDED.leadership_end_date,
            current_function_name           = EXCLUDED.current_function_name,
            function_location               = EXCLUDED.function_location,
            registration_number             = EXCLUDED.registration_number,
            ufmg_registration_number        = EXCLUDED.ufmg_registration_number,
            semester_reference              = EXCLUDED.semester_reference;
        """  # noqa: E501

    adm_database.execmany(SCRIPT_SQL, researcher.to_dict(orient="records"))
    return {
        "success": researcher.to_dict(orient="records"),
        "not_found": not_found.to_dict(orient="records"),
    }


def technician_basic_query(year, semester, departament):
    parameters = list()

    if year or semester:
        parameters.append(f"{year}.{semester}")
        filter_semester = """
            AND semester_reference = %s
            """
    else:
        filter_semester = """
            AND semester_reference = (SELECT MAX(semester_reference)
            FROM ufmg.technician)
            """

    SCRIPT_SQL = f"""
        SELECT
            technician_id,
            registration_number,
            ufmg_registration_number,
            full_name,
            gender,
            status_code,
            work_regime,
            job_class,
            job_title,
            job_rank,
            job_reference_code,
            academic_degree,
            department_name,
            academic_unit,
            organization_entry_date,
            last_promotion_date,
            semester_reference
        FROM
            ufmg.technician
        WHERE
            1 = 1
            {filter_semester}
        """

    registry = adm_database.select(SCRIPT_SQL, parameters)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "technician_id",
            "registration_number",
            "ufmg_registration_number",
            "full_name",
            "gender",
            "status_code",
            "work_regime",
            "job_class",
            "job_title",
            "job_rank",
            "job_reference_code",
            "academic_degree",
            "department_name",
            "academic_unit",
            "organization_entry_date",
            "last_promotion_date",
            "semester_reference",
        ],
    )
    return data_frame.to_dict(orient="records")


def technician_query_semester():
    SCRIPT_SQL = """
    SELECT
        SUBSTRING(semester_reference, 1, 4) AS year,
        SUBSTRING(semester_reference, 6, 1) AS semester
    FROM
        ufmg.technician
    GROUP BY semester_reference;
    """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(registry, columns=["year", "semester"])

    return data_frame.to_dict(orient="records")


def technician_insert_role(ListRole: ListRole):
    parameters = list()
    for role in ListRole.list_roles:
        parameters.append((role.role, role.researcher_id))

    SCRIPT_SQL = """
        INSERT INTO technician_role (role, technician_id)
        VALUES (%s, %s)
        """

    adm_database.exec(SCRIPT_SQL, parameters)


def technician_query_role():
    SCRIPT_SQL = """
        SELECT
            role,
            technician_id
        FROM
            technician_role
        """

    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.Dataframe(registry, columns=["role", "technician_id"])

    return data_frame.to_dict(orient="records")


def departament_technician_insert(
    ListTechnicianDepartament: ListTechnicianDepartament,
):
    parameters = list()

    for technician in ListTechnicianDepartament.list_technician:
        parameters.append((technician.dep_id, technician.technician_id))

    SCRIPT_SQL = """
    INSERT INTO ufmg.departament_technician (dep_id, technician_id)
    VALUES (%s, %s);
    """
    adm_database.execmany(SCRIPT_SQL, parameters)


def departament_technician_delete(technician):
    SCRIPT_SQL = """
    DELETE FROM ufmg.departament_technician
    WHERE technician_id = %s AND dep_id = %s;
    """

    adm_database.exec(
        SCRIPT_SQL, [technician[0]["technician_id"], technician[0]["dep_id"]]
    )


def technician_departament_basic_query(researcher_id):
    SCRIPT_SQL = """
    SELECT
        d.dep_id,
        org_cod,
        dep_nom,
        dep_des,
        dep_email,
        dep_site,
        dep_sigla,
        dep_tel,
        img_data
    FROM
        ufmg.departament d
        LEFT JOIN ufmg.departament_technician dtech
        ON dtech.dep_id = d.dep_id
    WHERE
        dtech.technician_id = %s;
    """

    registry = adm_database.select(SCRIPT_SQL, researcher_id)

    data_frame = pd.Dataframe(
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


def reacher_basic_query(year, semester):
    parameters = list()
    if year or semester:
        parameters.append(f"{year}.{semester}")
        filter_semester = """
            WHERE semester_reference = %s
            """
    else:
        filter_semester = """
            WHERE semester_reference = (SELECT MAX(semester_reference) FROM ufmg.researcher)
            """

    SCRIPT_SQL = f"""
        SELECT
            researcher_id,
            registration_number,
            ufmg_registration_number,
            full_name,
            gender,
            status_code,
            work_regime,
            job_class,
            job_title,
            job_rank,
            job_reference_code,
            academic_degree,
            organization_entry_date,
            last_promotion_date,
            employment_status_description,
            department_name,
            career_category,
            academic_unit,
            unit_code,
            function_code,
            position_code,
            leadership_start_date,
            leadership_end_date,
            current_function_name,
            function_location,
            semester_reference
        FROM
            ufmg.researcher
        {filter_semester}
        """

    registry = adm_database.select(SCRIPT_SQL, parameters)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "researcher_id",
            "registration_number",
            "ufmg_registration_number",
            "full_name",
            "gender",
            "status_code",
            "work_regime",
            "job_class",
            "job_title",
            "job_rank",
            "job_reference_code",
            "academic_degree",
            "organization_entry_date",
            "last_promotion_date",
            "employment_status_description",
            "department_name",
            "career_category",
            "academic_unit",
            "unit_code",
            "function_code",
            "position_code",
            "leadership_start_date",
            "leadership_end_date",
            "current_function_name",
            "function_location",
            "semester_reference",
        ],
    )
    return data_frame.to_dict(orient="records")


def teacher_query_semester():
    SCRIPT_SQL = """
    SELECT
        SUBSTRING(semester_reference, 1, 4) AS year,
        SUBSTRING(semester_reference, 6, 1) AS semester
    FROM
        ufmg.researcher
    GROUP BY semester_reference;
    """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(registry, columns=["year", "semester"])

    return data_frame.to_dict(orient="records")


def teacher_insert_role(ListRole: ListRole):
    parameters = list()
    for role in ListRole.list_roles:
        parameters.append((role.role, role.researcher_id))

    SCRIPT_SQL = """
        INSERT INTO researcher_role (role, researcher_id)
        VALUES (%s, %s)
        """

    adm_database.exec(SCRIPT_SQL, parameters)


def teacher_query_role():
    SCRIPT_SQL = """
        SELECT
            role,
            technician_id
        FROM
            technician_role
        """

    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.Dataframe(registry, columns=["role", "technician_id"])

    return data_frame.to_dict(orient="records")


def departament_insert(departaments, file):
    parameters = list()

    # Certifique-se de que 'menagers' está no dicionário e é uma lista,
    # e converta para o formato que o psycopg2 espera para arrays (list).
    # Se 'menagers' puder ser None, trate isso adequadamente.
    menagers = departaments.get("menagers")
    if menagers is None:
        menagers_db_format = None
    elif isinstance(menagers, list):
        menagers_db_format = menagers
    else:
        # Se 'menagers' não for uma lista ou None, pode ser necessário um tratamento de erro ou conversão
        raise ValueError(
            "O campo 'menagers' deve ser uma lista de strings ou None."
        )

    parameters = [
        departaments["dep_id"],
        departaments["org_cod"],
        departaments["dep_nom"],
        departaments["dep_des"],
        departaments["dep_email"],
        departaments["dep_site"],
        departaments["dep_sigla"],
        departaments["dep_tel"],
        psycopg2.Binary(file["img_data"].read()),
        menagers_db_format,  # Adicione os managers aqui
    ]
    SCRIPT_SQL = """
        INSERT INTO UFMG.departament
            (dep_id, org_cod, dep_nom, dep_des, dep_email, dep_site, dep_sigla,
             dep_tel, img_data, menagers) -- Adicione 'menagers' aqui
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) -- Adicione um placeholder para 'menagers'
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def departament_delete(dep_id):
    SCRIPT_SQL = """
        DELETE FROM UFMG.departament_researcher
        WHERE dep_id = %s;
        DELETE FROM UFMG.departament
        WHERE dep_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [dep_id, dep_id])


def departament_update(departament, file):
    parameters = list()
    filter_image = str()

    # Certifique-se de que 'menagers' está no dicionário e é uma lista,
    # e converta para o formato que o psycopg2 espera para arrays (list).
    menagers = departament.get("menagers")
    if menagers is None:
        menagers_db_format = None
    elif isinstance(menagers, list):
        menagers_db_format = menagers
    else:
        raise ValueError(
            "O campo 'menagers' deve ser uma lista de strings ou None."
        )

    # fmt: off
    parameters = [
        departament["org_cod"], departament["dep_nom"],
        departament["dep_des"], departament["dep_email"],
        departament["dep_site"], departament["dep_sigla"],
        departament["dep_tel"],
        menagers_db_format,
        departament["dep_id"],
    ]
    if file:
        image = psycopg2.Binary(file["img_data"].read())
        filter_image = "img_data = %s,"
        parameters.insert(7, image)

    # fmt: on
    SCRIPT_SQL = f"""
        UPDATE UFMG.departament
        SET org_cod = %s,
            dep_nom = %s,
            dep_des = %s,
            dep_email = %s,
            dep_site = %s,
            dep_sigla = %s,
            {filter_image}
            dep_tel = %s,
            menagers = %s -- Adicione 'menagers' aqui
        WHERE dep_id = %s
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def departament_researcher_query(dep_id):
    SCRIPT_SQL = """
    SELECT
        r.researcher_id,
        r.name,
        r.lattes_id
    FROM
        researcher r
    WHERE
        r.researcher_id IN (SELECT
                                researcher_id
                            FROM
                                ufmg.departament_researcher
                            WHERE dep_id = %s)
    """

    registry = adm_database.select(SCRIPT_SQL, [dep_id])

    data_frame = pd.DataFrame(
        registry, columns=["researcher_id", "name", "lattes_id"]
    )
    return data_frame.to_dict(orient="records")


def departament_insert_discipline(ListDiscipline: ListDiscipline):
    parameters = list()

    for discipline in ListDiscipline.list_discipline:
        professors_id = list()
        professors_name = list()
        professors_workload = list()
        for professor in discipline.professor:
            SCRIPT_SQL = """
            SELECT researcher_id FROM UFMG.researcher
            WHERE inscufmg = %s
            """
            researcher_id = adm_database.select(SCRIPT_SQL, [professor.ufmg_id])
            if researcher_id:
                professors_id.append(researcher_id[0][0])
            else:
                professors_id.append(None)
            professors_name.append(professor.name)
            professors_workload.append(professor.responsibility)

        parameters.append(
            (
                discipline.dep_id,
                discipline.semester,
                discipline.department,
                discipline.academic_activity_code,
                discipline.academic_activity_name,
                discipline.academic_activity_ch,
                discipline.demanding_courses,
                discipline.oft,
                discipline.id,
                discipline.available_slots,
                discipline.occupied_slots,
                discipline.percent_occupied_slots,
                discipline.schedule,
                discipline.language,
                professors_id,
                professors_workload,
                discipline.status,
                professors_name,
            )
        )

    SCRIPT_SQL = """
        INSERT INTO UFMG.disciplines
            (dep_id, semester, department, academic_activity_code,
            academic_activity_name, academic_activity_ch,
            demanding_courses, oft, id, available_slots, occupied_slots,
            percent_occupied_slots, schedule, language, researcher_id,
            workload, status, researcher_name)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    adm_database.execmany(SCRIPT_SQL, parameters)


def departament_query_discipline(dep_id):
    if dep_id:
        filter_departament = "WHERE dep_id = %s"
    else:
        filter_departament = str()
    SCRIPT_SQL = f"""
        SELECT
            semester, department, academic_activity_code,
            academic_activity_name, academic_activity_ch,
            demanding_courses, oft, id, available_slots, occupied_slots,
            percent_occupied_slots, schedule, language, researcher_id,
            workload, status, researcher_name
        FROM
            UFMG.disciplines
        {filter_departament}
        """

    registry = adm_database.select(SCRIPT_SQL, [dep_id])

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "semester",
            "department",
            "academic_activity_code",
            "academic_activity_name",
            "academic_activity_ch",
            "demanding_courses",
            "oft",
            "id",
            "available_slots",
            "occupied_slots",
            "percent_occupied_slots",
            "schedule",
            "language",
            "researcher_id",
            "workload",
            "status",
            "researcher_name",
        ],
    )

    return data_frame.to_dict(orient="records")


def departament_query_discipline_semester(dep_id):
    if dep_id:
        filter_departament = "WHERE dep_id = %s"
    else:
        filter_departament = str()

    SCRIPT_SQL = f"""
    SELECT
        SUBSTRING(semester, 1, 4) AS year,
        SUBSTRING(semester, 6, 1) AS semester
    FROM
        UFMG.disciplines
    {filter_departament}
    GROUP BY semester;
    """

    registry = adm_database.select(SCRIPT_SQL, [dep_id])

    data_frame = pd.DataFrame(registry, columns=["year", "semester"])

    return data_frame.to_dict(orient="records")
