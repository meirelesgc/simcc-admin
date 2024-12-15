import pandas as pd

pd.set_option("future.no_silent_downcasting", True)

from pydantic import UUID4

from ..dao import Connection
from ..models.graduate_program import ListGraduateProgram, GraduateProgram


adm_database = Connection()


def graduate_program_insert(ListGraduateProgram: ListGraduateProgram):
    parameters = list()

    # fmt: off
    for program in ListGraduateProgram.graduate_program_list:
        print(program)
        parameters.append((
            program.graduate_program_id, program.code, program.name,
            program.area, program.modality, program.type, program.rating,
            program.institution_id, program.city, program.url_image,
            program.acronym, program.description, program.visible, program.site
        ))
    # fmt: on

    SCRIPT_SQL = """
        INSERT INTO graduate_program
        (graduate_program_id, code, name, area, modality, type, rating,
        institution_id, city, url_image, acronym, description, visible, site)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    adm_database.execmany(SCRIPT_SQL, parameters)


def graduate_program_update(graduate_program_id: UUID4):
    parameters = [graduate_program_id]
    SCRIPT_SQL = """
        UPDATE graduate_program
        SET visible = NOT visible
        WHERE graduate_program_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_basic_query(institution_id: UUID4):
    parameters = [institution_id]
    SCRIPT_SQL = """
        SELECT
            gp.graduate_program_id,
            gp.code,
            gp.name,
            gp.area,
            gp.modality,
            gp.type,
            gp.rating,
            gp.institution_id,
            gp.description,
            gp.url_image,
            gp.acronym,
            gp.city,
            gp.visible,
            gp.site,
            COUNT(CASE WHEN gr.type_ = 'PERMANENTE' THEN 1 END) as qtd_permanente,
            COUNT(CASE WHEN gr.type_ = 'COLABORADOR' THEN 1 END) as qtd_colaborador
        FROM
            graduate_program gp
        LEFT JOIN
            graduate_program_researcher gr ON gp.graduate_program_id = gr.graduate_program_id
        WHERE
            gp.institution_id = %s
        GROUP BY
            gp.graduate_program_id, gp
        """

    registry = adm_database.select(SCRIPT_SQL, parameters)
    data_frame = pd.DataFrame(
        registry,
        columns=[
            "graduate_program_id",
            "code",
            "name",
            "area",
            "modality",
            "type",
            "rating",
            "institution_id",
            "description",
            "url_image",
            "acronym",
            "city",
            "visible",
            "site",
            "qtd_permanente",
            "qtd_colaborador",
        ],
    )

    SCRIPT_SQL = f"""
        SELECT 
            graduate_program_id,
            COUNT(researcher_id) as qtr_discente
        FROM 
            graduate_program_student 
        GROUP BY 
            graduate_program_id
        """
    registry = adm_database.select(SCRIPT_SQL)

    qtd_discentes = pd.DataFrame(
        registry, columns=["graduate_program_id", "qtd_discente"])

    data_frame = pd.merge(
        data_frame,
        qtd_discentes,
        how="left",
        on="graduate_program_id",
    )
    data_frame.fillna(0, inplace=True)

    return data_frame.to_dict(orient="records")


def graduate_program_delete(graudate_program_id: UUID4):
    parameters = [
        graudate_program_id, graudate_program_id, graudate_program_id
    ]
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
        program.code, program.name, program.area,
        program.modality, program.type,
        program.rating, program.institution_id,
        program.city, program.url_image,
        program.acronym, program.description,
        program.visible, program.site,
        program.graduate_program_id,
    )
    # fmt: on
    SCRIPT_SQL = """
        UPDATE graduate_program SET
        code = %s, name = %s, area = %s, modality = %s, type = %s,
        rating = %s, institution_id = %s, city = %s, url_image = %s,
        acronym = %s, description = %s, visible = %s, site = %s
        WHERE graduate_program_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, parameters)


def graduate_program_count(institution_id: UUID4 = None):
    parameters = list()
    filter_institution = str()
    if institution_id:
        filter_institution = "WHERE institution_id = %s"
        parameters.extend([institution_id])

    SCRIPT_SQL = f"SELECT COUNT(*) FROM graduate_program {filter_institution}"

    registry = adm_database.select(SCRIPT_SQL, parameters)

    # psycopg2 retorna uma lista de truplas,
    # quero apenas o primeiro valor da primeira lista
    return registry[0][0]
