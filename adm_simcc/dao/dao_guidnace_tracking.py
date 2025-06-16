import pandas as pd
from pydantic import UUID4

from ..dao import Connection

adm_database = Connection()


def get_all_guidance_trackings():
    SCRIPT_SQL = """
        SELECT 
            id,
            student_researcher_id,
            supervisor_researcher_id,
            co_supervisor_researcher_id,
            graduate_program_id,
            start_date,
            planned_date_project,
            done_date_project,
            planned_date_qualification,
            done_date_qualification,
            planned_date_conclusion,
            done_date_conclusion,
            created_at,
            updated_at,
            deleted_at
        FROM guidance_tracking
        WHERE deleted_at IS NULL
        ORDER BY created_at DESC;
    """
    records = adm_database.select(SCRIPT_SQL)
    columns = [
        "id",
        "student_researcher_id",
        "supervisor_researcher_id",
        "co_supervisor_researcher_id",
        "graduate_program_id",
        "start_date",
        "planned_date_project",
        "done_date_project",
        "planned_date_qualification",
        "done_date_qualification",
        "planned_date_conclusion",
        "done_date_conclusion",
        "created_at",
        "updated_at",
        "deleted_at",
    ]
    df = pd.DataFrame(records, columns=columns)
    return df.to_dict(orient="records"), 200


def get_guidance_tracking_by_id(guidance_id: UUID4):
    SCRIPT_SQL = """
        SELECT 
            id,
            student_researcher_id,
            supervisor_researcher_id,
            co_supervisor_researcher_id,
            graduate_program_id,
            start_date,
            planned_date_project,
            done_date_project,
            planned_date_qualification,
            done_date_qualification,
            planned_date_conclusion,
            done_date_conclusion,
            created_at,
            updated_at,
            deleted_at
        FROM guidance_tracking
        WHERE id = %(guidance_id)s AND deleted_at IS NULL;
    """
    params = {"guidance_id": guidance_id}
    result = adm_database.select(SCRIPT_SQL, params)
    if not result:
        return {"message": "Registro não encontrado."}, 404
    columns = [
        "id",
        "student_researcher_id",
        "supervisor_researcher_id",
        "co_supervisor_researcher_id",
        "graduate_program_id",
        "start_date",
        "planned_date_project",
        "done_date_project",
        "planned_date_qualification",
        "done_date_qualification",
        "planned_date_conclusion",
        "done_date_conclusion",
        "created_at",
        "updated_at",
        "deleted_at",
    ]
    df = pd.DataFrame(result, columns=columns)
    return df.to_dict(orient="records")[0], 200


def create_guidance_tracking(data: dict):
    SCRIPT_SQL = """
        INSERT INTO guidance_tracking (
            student_researcher_id,
            supervisor_researcher_id,
            co_supervisor_researcher_id,
            graduate_program_id,
            start_date,
            planned_date_project,
            done_date_project,
            planned_date_qualification,
            done_date_qualification,
            planned_date_conclusion,
            done_date_conclusion,
            created_at
        ) VALUES (
            %(student_researcher_id)s,
            %(supervisor_researcher_id)s,
            %(co_supervisor_researcher_id)s,
            %(graduate_program_id)s,
            %(start_date)s,
            %(planned_date_project)s,
            %(done_date_project)s,
            %(planned_date_qualification)s,
            %(done_date_qualification)s,
            %(planned_date_conclusion)s,
            %(done_date_conclusion)s,
            NOW()
        );
    """
    adm_database.exec(SCRIPT_SQL, data)
    return {"message": "Registro criado com sucesso."}, 201


def update_guidance_tracking(guidance_id: UUID4, data: dict):
    SCRIPT_SQL = """
        UPDATE guidance_tracking SET
            student_researcher_id = %(student_researcher_id)s,
            supervisor_researcher_id = %(supervisor_researcher_id)s,
            co_supervisor_researcher_id = %(co_supervisor_researcher_id)s,
            graduate_program_id = %(graduate_program_id)s,
            start_date = %(start_date)s,
            planned_date_project = %(planned_date_project)s,
            done_date_project = %(done_date_project)s,
            planned_date_qualification = %(planned_date_qualification)s,
            done_date_qualification = %(done_date_qualification)s,
            planned_date_conclusion = %(planned_date_conclusion)s,
            done_date_conclusion = %(done_date_conclusion)s,
            updated_at = NOW()
        WHERE id = %(guidance_id)s AND deleted_at IS NULL;
    """
    params = data.copy()
    params["guidance_id"] = guidance_id
    adm_database.exec(SCRIPT_SQL, params)
    return {"message": "Registro atualizado com sucesso."}, 200


def delete_guidance_tracking(guidance_id: UUID4):
    SCRIPT_SQL = """
        UPDATE guidance_tracking
        SET deleted_at = NOW()
        WHERE id = %(guidance_id)s AND deleted_at IS NULL;
    """
    params = {"guidance_id": guidance_id}
    adm_database.exec(SCRIPT_SQL, params)
    return {"message": "Registro excluído com sucesso."}, 200
