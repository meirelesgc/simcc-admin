import re
import unicodedata
from uuid import uuid4

import pandas as pd
from numpy import nan

from ..dao import Connection
from ..models.teachers import ListRole
from ..models.technician import ListTechnicianDepartament

adm_database = Connection()


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


def departament_basic_query(dep_id):
    departament_filter = str()
    if dep_id:
        departament_filter = "WHERE dep_id = %s"

    SCRIPT_SQL = f"""
        WITH researchers AS (
                SELECT dep_id, ARRAY_AGG(r.name) AS researchers
            FROM ufmg.departament_researcher dr
                LEFT JOIN researcher r ON dr.researcher_id = r.researcher_id
            GROUP BY dep_id
            HAVING COUNT(r.researcher_id) >= 1
        )
        SELECT
            dp.dep_id, dp.org_cod, dp.dep_nom, dp.dep_des, dp.dep_email, dp.dep_site, dp.dep_sigla,
            dp.dep_tel, dp.img_data, COALESCE(r.researchers, ARRAY[]::text[]) AS researchers
        FROM
            UFMG.departament dp
        LEFT JOIN researchers r
            ON r.dep_id = dp.dep_id
        {departament_filter};
        """
    reg = adm_database.select(SCRIPT_SQL, [dep_id])

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
    ]
    result = list()
    for row in reg:
        row_dict = dict(zip(columns, row))
        row_dict["img_data"] = None
        result.append(row_dict)

    return result


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
