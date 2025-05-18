import pandas as pd

from ..dao import Connection
from ..models.technician import (
    ListRole,
    ListTechnicianDepartament,
)

adm_database = Connection()


def technician_basic_query(year, semester, departament):
    parameters = list()

    if year or semester:
        parameters.append(f"{year}.{semester}")
        filter_semester = """
            AND semester_reference = %s
            """
    else:
        filter_semester = """
            AND semester_reference = (SELECT MAX(semester_reference) FROM ufmg.technician)
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
