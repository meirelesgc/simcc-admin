import pandas as pd
from adm_simcc.dao import Connection
from psycopg2.errors import UniqueViolation


def get_researcher_id(researcher_name):
    SCRIPT_SQL = """
        SELECT researcher_id
        FROM researcher
        WHERE regexp_replace(
                unaccent(upper(name)),
                '[^A-Z0-9]',
                '',
                'g'
            ) = regexp_replace(
                unaccent(upper(%(name)s)),
                '[^A-Z0-9]',
                '',
                'g'
            )
    """
    researcher = Connection().select(SCRIPT_SQL, {"name": researcher_name})
    if researcher:
        return researcher[0][0]
    return None


def get_program_id(code):
    SCRIPT_SQL = """
        SELECT graduate_program_id
        FROM graduate_program
        WHERE code = %(code)s
        """
    program = Connection().select(SCRIPT_SQL, {"code": code})
    if program:
        return program[0][0]
    return None


researchers = pd.read_csv("files/researchers.csv")


for _, researcher in researchers.iterrows():
    r_id = get_researcher_id(researcher["nome"])
    if r_id:
        pg_id = get_program_id(researcher["id do programa"])
        if pg_id:
            SCRIPT_SQL = """
                INSERT INTO public.graduate_program_researcher(
                graduate_program_id, researcher_id, year, type_)
                VALUES (%(pg_id)s, %(r_id)s, ARRAY[2025, 2024, 2023, 2022, 2021],
                %(categoria)s);
                """
            if "PERMANENTE" in researcher["categoria"]:
                categoria = "PERMANENTE"
            else:
                categoria = "COLABORADOR"

            try:
                Connection().exec(
                    SCRIPT_SQL,
                    {"pg_id": pg_id, "r_id": r_id, "categoria": categoria},
                )
            except UniqueViolation:
                print("Duplicado")
