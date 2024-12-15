import pandas as pd

from ..dao import Connection
from ..models.student import GraduateProgramStudent, ListGraduateProgramStudent

adm_database = Connection()


def student_insert(ListStudent: ListGraduateProgramStudent):
    for student in ListStudent.student_list:
        SCRIPT_SQL = """
            SELECT researcher_id FROM researcher
            WHERE lattes_id = %(lattes_id)s
            """
        student_id = adm_database.select(SCRIPT_SQL, student.model_dump())
        if student_id:
            student.student_id = student_id[0][0]
        else:
            researcher_student_insert(student)

    SCRIPT_SQL = """
        INSERT INTO public.graduate_program_student(
        graduate_program_id, researcher_id, year)
        VALUES (%(graduate_program_id)s, %(student_id)s, %(year)s);
        """
    adm_database.execmany(SCRIPT_SQL, ListStudent.model_dump()["student_list"])


def researcher_student_insert(student: GraduateProgramStudent):
    SCRIPT_SQL = """
        INSERT INTO public.researcher(
        researcher_id, name, lattes_id, institution_id)
        VALUES (%(student_id)s, %(name)s, %(lattes_id)s, %(institution_id)s);
        """
    adm_database.exec(SCRIPT_SQL, student.model_dump())


def student_basic_query(
    graduate_program_id: str = None,
    institution_id: str = None,
    lattes_id: str = None,
):
    if lattes_id:
        filter_lattes_id = f"AND r.lattes_id = '{lattes_id}'"
    else:
        filter_lattes_id = str()

    if graduate_program_id:
        filter_graduate_program = (
            f"AND gps.graduate_program_id = '{graduate_program_id}'"
        )
    else:
        filter_graduate_program = str()

    if institution_id:
        filter_institution = f"AND r.institution_id = '{institution_id}'"
    else:
        filter_institution = str()

    SCRIPT_SQL = f"""
        SELECT
            r.name,
            r.lattes_id,
            'DISCENTE' as type_,
            gps.year
        FROM
            graduate_program_student gps
        LEFT JOIN researcher r ON
        r.researcher_id = gps.researcher_id
        WHERE
            1 = 1
            {filter_graduate_program}
            {filter_institution}
            {filter_lattes_id};
    """
    registry = adm_database.select(SCRIPT_SQL)
    data_frame = pd.DataFrame(
        registry,
        columns=[
            "name",
            "lattes_id",
            "type_",
            "years",
        ],
    )

    return data_frame.to_dict(orient="records")


def student_delete(student_id, graduate_program):
    SCRIPT_SQL = f"""
        DELETE FROM graduate_program_student gs
        USING researcher r
        WHERE gs.researcher_id = r.researcher_id
            AND r.lattes_id = '{student_id}'
            AND gs.graduate_program_id = '{graduate_program}';
        DELETE FROM researcher WHERE lattes_id = '{student_id}';
        """
    adm_database.exec(SCRIPT_SQL)


def student_update(
    ListGraduateProgramStudent: ListGraduateProgramStudent,
):
    parameters = list()

    # fmt: 0ff
    for researcher in ListGraduateProgramStudent.student_list:
        parameters.append(
            (
                researcher.year,
                researcher.lattes_id,
                researcher.graduate_program_id,
            )
        )
    # fmt: on

    SCRIPT_SQL = """
        UPDATE graduate_program_student AS gps
        SET
            year = %s
        FROM researcher AS r
        WHERE
            gps.researcher_id = r.researcher_id
            AND r.lattes_id = %s
            AND gps.graduate_program_id = %s;
        """
    adm_database.execmany(SCRIPT_SQL, parameters)
