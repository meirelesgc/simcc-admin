from typing import Optional
from uuid import UUID

import pandas as pd

from ..dao import Connection
from ..models.graduate_program import GraduateProgram, ListGraduateProgram

pd.set_option("future.no_silent_downcasting", True)


adm_database = Connection()


def graduate_program_insert(list_graduate_program: ListGraduateProgram):
    """
    Insere uma lista de novos programas de pós-graduação no banco de dados.
    """
    parameters = []
    # fmt: off
    for program in list_graduate_program.graduate_program_list:
        parameters.append((
            program.graduate_program_id, program.code, program.name, program.name_en,
            program.basic_area, program.cooperation_project, program.area, program.modality,
            program.type, program.rating, program.institution_id, program.state, program.city,
            program.region, program.url_image, program.acronym, program.description,
            program.visible, program.site, program.coordinator, program.email, program.start,
            program.phone, program.periodicity
        ))
    # fmt: on

    SCRIPT_SQL = """
        INSERT INTO graduate_program (
            graduate_program_id, code, name, name_en, basic_area, cooperation_project,
            area, modality, type, rating, institution_id, state, city, region,
            url_image, acronym, description, visible, site, coordinator, email,
            start_date, phone, periodicity
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
        SELECT
            gp.graduate_program_id, gp.code, gp.name, gp.name_en, gp.basic_area,
            gp.cooperation_project, gp.area, gp.modality, gp.type, gp.rating,
            gp.institution_id, gp.state, gp.city, gp.region, gp.url_image,
            gp.acronym, gp.description, gp.visible, gp.site, gp.coordinator,
            gp.email, gp.start, gp.phone, gp.periodicity, gp.created_at, gp.updated_at,
            COUNT(CASE WHEN gr.type_ = 'PERMANENTE' THEN 1 END) as qtd_permanente,
            COUNT(CASE WHEN gr.type_ = 'COLABORADOR' THEN 1 END) as qtd_colaborador
        FROM
            graduate_program gp
        LEFT JOIN
            graduate_program_researcher gr ON gp.graduate_program_id = gr.graduate_program_id
            {join_menager}
        WHERE 1 = 1
            {filter_institution}
            {filter_graduate_program}
            {filter_menager}
        GROUP BY
            gp.graduate_program_id
    """

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
        "created_at",
        "updated_at",
        "qtd_permanente",
        "qtd_colaborador",
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
        data_frame["qtd_discente"].fillna(0, inplace=True)
    else:
        data_frame["qtd_discente"] = 0

    data_frame.fillna(0, inplace=True)

    return data_frame.to_dict(orient="records")


def graduate_program_delete(graduate_program_id: UUID):
    """
    Deleta um programa de pós-graduação e seus registros associados.
    """
    # A lógica de DELETE não muda, pois as chaves estrangeiras garantem
    # a remoção em cascata ou você continua deletando com base no ID.
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
    """
    Atualiza todas as informações de um programa de pós-graduação.
    """
    # fmt: off
    parameters = (
        program.code, program.name, program.name_en, program.basic_area,
        program.cooperation_project, program.area, program.modality, program.type,
        program.rating, program.institution_id, program.state, program.city,
        program.region, program.url_image, program.acronym, program.description,
        program.visible, program.site, program.coordinator, program.email,
        program.start, program.phone, program.periodicity,
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
            updated_at = CURRENT_TIMESTAMP
        WHERE graduate_program_id = %s;
    """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_count(institution_id=None):
    """
    Conta o número de programas de pós-graduação, com filtro opcional por instituição.
    """
    # Esta função não precisa de alterações, pois conta linhas inteiras.
    parameters = []
    filter_institution = ""
    if institution_id:
        filter_institution = "WHERE institution_id = %s"
        parameters.append(institution_id)

    SCRIPT_SQL = f"SELECT COUNT(*) FROM graduate_program {filter_institution}"

    registry = adm_database.select(SCRIPT_SQL, parameters)

    return registry[0][0]
