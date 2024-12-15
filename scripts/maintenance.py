import os

import pandas as pd
import psycopg2

from adm_simcc.dao import Connection

database = Connection()


def import_researcher(file_path):
    SCRIPT_SQL = """
        INSERT INTO researcher (name, lattes_id, institution_id)
        SELECT %s, %s, institution_id
        FROM institution
        WHERE acronym = %s;
        """
    dataframe = pd.read_csv(
        file_path, sep=",", quotechar='"', doublequote=True, escapechar="\\"
    )
    dataframe["acronym"] = dataframe["acronym"].fillna("UICL")
    for k, researcher in dataframe.iterrows():
        try:
            database.exec(
                SCRIPT_SQL,
                [
                    researcher["name"],
                    researcher["lattes_id"],
                    researcher["acronym"],
                ],
            )
        except psycopg2.errors.UniqueViolation:
            print(researcher)


def import_graduate_program(file_path):
    SCRIPT_SQL = """
        INSERT INTO graduate_program (
            code,
            name,
            area,
            modality,
            type,
            rating,
            institution_id,
            state,
            city,
            region,
            url_image,
            description,
            visible,
            site,
            acronym
        )
        SELECT %s, %s, %s, %s, %s, %s, institution_id, %s, %s, %s, %s, %s, %s, %s, %s
        FROM institution
        WHERE acronym = %s;
    """

    dataframe = pd.read_csv(
        file_path, sep=",", quotechar='"', doublequote=True, escapechar=None
    )
    dataframe = dataframe.fillna("")
    for k, graduate_program in dataframe.iterrows():
        database.exec(
            SCRIPT_SQL,
            [
                graduate_program["code"],
                graduate_program["name"],
                graduate_program["area"],
                graduate_program["modality"],
                graduate_program["type"],
                graduate_program["rating"],
                graduate_program["state"],
                graduate_program["city"],
                graduate_program["region"],
                graduate_program["url_image"],
                graduate_program["description"],
                graduate_program["visible"],
                graduate_program["site"],
                graduate_program["acronym"],
                graduate_program["i.acronym"],
            ],
        )


def import_graduate_program_researcher(file_path):
    SCRIPT_SQL = """
    INSERT INTO
        public.graduate_program_researcher (
            graduate_program_id,
            researcher_id,
            type_
        )
    SELECT
        graduate_program_id,
        researcher_id,
        %s
    FROM
        researcher,
        graduate_program
    WHERE
        lattes_id = %s
        AND code = %s;
    """
    dataframe = pd.read_csv(
        file_path, sep=",", quotechar='"', doublequote=True, escapechar="\\"
    )
    dataframe["lattes_id"] = dataframe["lattes_id"].astype("str")
    for k, graduate_program_researcher in dataframe.iterrows():
        try:
            database.exec(
                SCRIPT_SQL,
                [
                    graduate_program_researcher["type_"],
                    graduate_program_researcher["lattes_id"],
                    graduate_program_researcher["code"],
                ],
            )
        except Exception:
            print(graduate_program_researcher)


def import_graduate_program_student(file_path):
    SCRIPT_SQL = """
    INSERT INTO
        public.graduate_program_researcher (
            graduate_program_id,
            researcher_id
        )
    SELECT
        graduate_program_id,
        researcher_id
    FROM
        researcher,
        graduate_program
    WHERE
        lattes_id = %s
        AND code = %s;
    """
    dataframe = pd.read_csv(
        file_path, sep=",", quotechar='"', doublequote=True, escapechar="\\"
    )
    dataframe["lattes_id"] = dataframe["lattes_id"].astype("str")
    for k, graduate_program_student in dataframe.iterrows():
        database.exec(
            SCRIPT_SQL,
            [
                graduate_program_student["lattes_id"],
                graduate_program_student["code"],
            ],
        )


def select_file():
    files = os.listdir("files")
    for k, file in enumerate(files):
        print(f"[{k}] - {file}")
    choice = int(input("codigo do arquivo: "))
    return f"files/{files[choice]}"


if __name__ == "__main__":
    # file_path = select_file()
    # import_researcher(file_path)
    file_path = select_file()
    import_graduate_program(file_path)
    # file_path = select_file()
    # import_graduate_program_researcher(file_path)
    # file_path = select_file()
    # import_graduate_program_student(file_path)
