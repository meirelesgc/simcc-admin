import base64

import pandas as pd
import psycopg2

from ..dao import Connection
from ..models.departament import ListDiscipline

adm_database = Connection()


def departament_insert(departaments, file):
    parameters = list()

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
    ]
    SCRIPT_SQL = """
        INSERT INTO UFMG.departament
            (dep_id, org_cod, dep_nom, dep_des, dep_email, dep_site, dep_sigla,
             dep_tel, img_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def departament_basic_query(dep_id):
    departament_filter = str()
    if dep_id:
        departament_filter = "WHERE dep_id = %s"

    SCRIPT_SQL = f"""
        SELECT
            dep_id, org_cod, dep_nom, dep_des, dep_email, dep_site, dep_sigla,
            dep_tel, img_data
        FROM
            UFMG.departament
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
        row_dict["img_data"] = (
            base64.b64encode(row_dict["img_data"]).decode("utf-8")
            if row_dict["img_data"]
            else None
        )
        result.append(row_dict)

    return result


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
    # fmt: off
    parameters = [
        departament["org_cod"], departament["dep_nom"],
        departament["dep_des"], departament["dep_email"],
        departament["dep_site"], departament["dep_sigla"],
        departament["dep_tel"], departament["dep_id"],
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
            dep_tel = %s
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
