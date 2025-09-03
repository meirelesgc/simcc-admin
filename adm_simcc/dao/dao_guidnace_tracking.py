from datetime import datetime

import pandas as pd
from pandas import NaT
from pydantic import UUID4

from ..dao import Connection

adm_database = Connection()


def get_all_guidance_trackings(data):
    filters = str()

    if data.get("supervisor_researcher_id"):
        filters += """
            AND supervisor_researcher_id = %(supervisor_researcher_id)s
            """
    if data.get("graduate_program_id"):
        filters += """
            AND graduate_program_id = %(graduate_program_id)s
            """

    SCRIPT_SQL = f"""
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
            done_date_conclusion
        FROM guidance_tracking
        WHERE deleted_at IS NULL
            {filters}
        ORDER BY created_at DESC;
    """
    records = adm_database.select(SCRIPT_SQL, data)
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
    ]
    df = pd.DataFrame(records, columns=columns)
    if df.empty:
        return []

    today = datetime.now().date()

    def peding_days(student):
        if not student["done_date_project"]:
            planned = student["planned_date_project"]
            return (planned - today).days if planned else None

        if not student["done_date_qualification"]:
            planned = student["planned_date_qualification"]
            return (planned - today).days if planned else None

        if not student["done_date_conclusion"]:
            planned = student["planned_date_conclusion"]
            return (planned - today).days if planned else None

        done_conclusion = student["done_date_conclusion"]
        if done_conclusion:
            return (today - done_conclusion).days

    def peding_days_(row):
        delays = []
        if row["done_date_conclusion"] is None:
            if row["planned_date_conclusion"] < today:
                days = (today - row["planned_date_conclusion"]).days
                delays.append(days)
        if row["done_date_qualification"] is None:
            if row["planned_date_qualification"] < today:
                days = (today - row["planned_date_qualification"]).days
                delays.append(days)
        if row["done_date_project"] is None:
            if row["planned_date_project"] < today:
                days = (today - row["planned_date_project"]).days
                delays.append(days)
        if delays:
            return max(delays)
        return 0

    def pending(row):
        if peding_days_(row) > 0:
            return "EM ATRASO"
        return "EM DIA"

    def type_(row):
        if row["done_date_project"] is None:
            return "PROJETO"
        if row["done_date_qualification"] is None:
            return "QUALIFICAÇÃO"
        if row["done_date_conclusion"] is None:
            return "CONCLUSÃO"
        return "FINALIZADO"

    df["peding_days"] = df.apply(peding_days, axis=1)
    df["peding"] = df.apply(pending, axis=1)
    df["type"] = df.apply(type_, axis=1)

    df = df.replace(NaT, None)

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
            done_date_conclusion
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
            %(done_date_conclusion)s
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


def create_guidance_config(data: dict):
    SCRIPT_SQL = """
        INSERT INTO guidance_config (
            duration_project_months,
            duration_qualification_months,
            duration_conclusion_months,
            config_name
        ) VALUES (
            %(duration_project_months)s,
            %(duration_qualification_months)s,
            %(duration_conclusion_months)s,
            %(config_name)s);
    """
    adm_database.exec(SCRIPT_SQL, data)
    return {"message": "Configuração criada com sucesso."}, 201


def get_all_guidance_configs(data: dict):
    filters = str()

    if data.get("config_name"):
        filters += " AND config_name = %(config_name)s"

    SCRIPT_SQL = f"""
        SELECT
            id,
            duration_project_months,
            duration_qualification_months,
            duration_conclusion_months,
            config_name,
            created_at,
            updated_at
        FROM guidance_config
        WHERE 1=1
            {filters}
        ORDER BY created_at DESC;
    """
    records = adm_database.select(SCRIPT_SQL, data)
    columns = [
        "id",
        "duration_project_months",
        "duration_qualification_months",
        "duration_conclusion_months",
        "config_name",
        "created_at",
        "updated_at",
    ]
    df = pd.DataFrame(records, columns=columns)
    return df.to_dict(orient="records"), 200


def update_guidance_config(data: dict):
    SCRIPT_SQL = """
        UPDATE guidance_config SET
            duration_project_months = %(duration_project_months)s,
            duration_qualification_months = %(duration_qualification_months)s,
            duration_conclusion_months = %(duration_conclusion_months)s,
            config_name = %(config_name)s,
            updated_at = NOW()
        WHERE id = %(config_id)s;
    """
    params = data.copy()
    params["config_id"] = data.get("id")
    adm_database.exec(SCRIPT_SQL, params)
    return {"message": "Configuração atualizada com sucesso."}, 200


def delete_guidance_config(config_id: UUID4):
    SCRIPT_SQL = """
        DELETE FROM guidance_config
        WHERE id = %(config_id)s;
    """
    params = {"config_id": config_id}
    adm_database.exec(SCRIPT_SQL, params)
    return {"message": "Configuração excluída com sucesso."}, 200
