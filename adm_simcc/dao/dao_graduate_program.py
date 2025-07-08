from typing import Optional
from uuid import UUID

import pandas as pd

from ..dao import Connection
from ..models.graduate_program import GraduateProgram, ListGraduateProgram

pd.set_option("future.no_silent_downcasting", True)


adm_database = Connection()


def graduate_program_insert(list_graduate_program: ListGraduateProgram):
    parameters = []
    # fmt: off
    for program in list_graduate_program.graduate_program_list:
        parameters.append((
            program.graduate_program_id, program.code, program.name, program.name_en,
            program.basic_area, program.cooperation_project, program.area, program.modality,
            program.type, program.rating, program.institution_id, program.state, program.city,
            program.region, program.url_image, program.acronym, program.description,
            program.visible, program.site, program.coordinator, program.email, program.start,
            program.phone, program.periodicity,
            program.menagers  # Adicione o campo menagers aqui
        ))
    # fmt: on

    SCRIPT_SQL = """
        INSERT INTO graduate_program (
            graduate_program_id, code, name, name_en, basic_area, cooperation_project,
            area, modality, type, rating, institution_id, state, city, region,
            url_image, acronym, description, visible, site, coordinator, email,
            start_date, phone, periodicity,
            menagers -- Adicione o nome da coluna aqui
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s -- Adicione um placeholder para o novo campo
        );
    """
    adm_database.execmany(SCRIPT_SQL, parameters)


def graduate_program_update(graduate_program_id: UUID):
    """
    Alterna a visibilidade de um programa de pós-graduação.
    """
    parameters = [graduate_program_id]
    SCRIPT_SQL = """
        UPDATE graduate_program
        SET
            visible = NOT visible,
            updated_at = CURRENT_TIMESTAMP
        WHERE graduate_program_id = %s;
    """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_basic_query(
    institution_id: UUID,
    user_id: UUID,
    graduate_program_id: Optional[UUID] = None,
):
    parameters = {}
    filter_institution = ""
    if institution_id:
        filter_institution = "AND gp.institution_id = %(institution_id)s"
        parameters["institution_id"] = institution_id

    filter_graduate_program = ""
    if graduate_program_id:
        filter_graduate_program = (
            "AND gp.graduate_program_id = %(graduate_program_id)s"
        )
        parameters["graduate_program_id"] = graduate_program_id

    join_menager = str()
    filter_menager = str()
    if user_id:
        join_menager = "INNER JOIN users u ON u.email = ANY(gp.menagers)"
        filter_menager = "AND u.user_id = %(user_id)s"
        parameters["user_id"] = user_id

    SCRIPT_SQL = f"""
        WITH permanent AS (
            SELECT graduate_program_id, COUNT(*) AS qtd_permanente
            FROM graduate_program_researcher
            WHERE type_ = 'PERMANENTE'
            GROUP BY graduate_program_id
        ),
        collaborators AS (
            SELECT graduate_program_id, COUNT(*) AS qtd_colaborador
            FROM graduate_program_researcher
            WHERE type_ = 'COLABORADOR'
            GROUP BY graduate_program_id
        ),
        students AS (
            SELECT graduate_program_id, COUNT(*) AS qtd_estudantes
            FROM graduate_program_student
            GROUP BY graduate_program_id
        ),
        researchers AS (
            SELECT graduate_program_id, ARRAY_AGG(r.name) AS researchers
            FROM graduate_program_researcher gpr
                LEFT JOIN researcher r ON gpr.researcher_id = r.researcher_id
            GROUP BY graduate_program_id
            HAVING COUNT(r.researcher_id) >= 1
        )
        SELECT gp.graduate_program_id, code, gp.name, gp.name_en, gp.basic_area,
            gp.cooperation_project, UPPER(area) AS area, UPPER(modality) AS modality,
            INITCAP(type) AS type, rating, i.institution_id, state, UPPER(city) AS city,
            region, url_image, gp.acronym, gp.description, visible, site,
            gp.coordinator, gp.email, gp.start, gp.phone, gp.periodicity,
            qtd_permanente, qtd_colaborador, qtd_estudantes, i.name AS institution,
            COALESCE(r.researchers, ARRAY[]::text[]) AS researchers, gp.menagers, gp.created_at,
			gp.updated_at
        FROM public.graduate_program gp
            LEFT JOIN permanent p
                ON gp.graduate_program_id = p.graduate_program_id
            LEFT JOIN students s
                ON gp.graduate_program_id = s.graduate_program_id
            LEFT JOIN collaborators c
                ON gp.graduate_program_id = c.graduate_program_id
            LEFT JOIN institution i
                ON i.institution_id = gp.institution_id
            LEFT JOIN researchers r
                ON r.graduate_program_id = gp.graduate_program_id
            {join_menager}
        WHERE 1 = 1
            {filter_menager}
            {filter_graduate_program}
            {filter_institution}
    """
    print(SCRIPT_SQL, parameters)
    registry = adm_database.select(SCRIPT_SQL, parameters)
    columns = [
        "graduate_program_id",
        "code",
        "name",
        "name_en",
        "basic_area",
        "cooperation_project",
        "area",
        "modality",
        "type",
        "rating",
        "institution_id",
        "state",
        "city",
        "region",
        "url_image",
        "acronym",
        "description",
        "visible",
        "site",
        "coordinator",
        "email",
        "start",
        "phone",
        "periodicity",
        "qtd_permanente",
        "qtd_colaborador",
        "qtd_estudantes",
        "institution",
        "researchers",
        "menagers",
        "created_at",
        "updated_at",
    ]

    data_frame = pd.DataFrame(registry, columns=columns)

    SCRIPT_SQL_STUDENTS = """
        SELECT
            graduate_program_id,
            COUNT(researcher_id) as qtr_discente
        FROM
            graduate_program_student
        GROUP BY
            graduate_program_id
    """
    registry_students = adm_database.select(SCRIPT_SQL_STUDENTS)

    qtd_discentes = pd.DataFrame(
        registry_students, columns=["graduate_program_id", "qtd_discente"]
    )

    if not qtd_discentes.empty:
        data_frame = pd.merge(
            data_frame,
            qtd_discentes,
            how="left",
            on="graduate_program_id",
        )
    else:
        data_frame["qtd_discente"] = 0

    data_frame.fillna(0, inplace=True)

    return data_frame.to_dict(orient="records")


def graduate_program_delete(graduate_program_id: UUID):
    parameters = [graduate_program_id, graduate_program_id, graduate_program_id]
    SCRIPT_SQL = """
        DELETE FROM graduate_program_student
        WHERE graduate_program_id = %s;
        DELETE FROM graduate_program_researcher
        WHERE graduate_program_id = %s;
        DELETE FROM graduate_program
        WHERE graduate_program_id = %s;
    """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_fix(program: GraduateProgram):
    # fmt: off
    parameters = (
        program.code, program.name, program.name_en, program.basic_area,
        program.cooperation_project, program.area, program.modality, program.type,
        program.rating, program.institution_id, program.state, program.city,
        program.region, program.url_image, program.acronym, program.description,
        program.visible, program.site, program.coordinator, program.email,
        program.start, program.phone, program.periodicity,
        program.menagers,
        program.graduate_program_id,
    )
    # fmt: on

    SCRIPT_SQL = """
        UPDATE graduate_program SET
            code = %s, name = %s, name_en = %s, basic_area = %s, cooperation_project = %s,
            area = %s, modality = %s, type = %s, rating = %s, institution_id = %s,
            state = %s, city = %s, region = %s, url_image = %s, acronym = %s,
            description = %s, visible = %s, site = %s, coordinator = %s,
            email = %s, start = %s, phone = %s, periodicity = %s,
            menagers = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE graduate_program_id = %s;
    """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_count(institution_id=None):
    # Esta função não precisa de alterações, pois conta linhas inteiras.
    parameters = []
    filter_institution = ""
    if institution_id:
        filter_institution = "WHERE institution_id = %s"
        parameters.append(institution_id)

    SCRIPT_SQL = f"SELECT COUNT(*) FROM graduate_program {filter_institution}"

    registry = adm_database.select(SCRIPT_SQL, parameters)

    return registry[0][0]
