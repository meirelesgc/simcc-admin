import ast
import unicodedata

import pandas as pd

from adm_simcc.dao import Connection


def normalize_keys(d):
    def normalize(s):
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower()

    return {normalize(k): v for k, v in d.items()}


programs = pd.read_csv("files/programs.csv")
print(programs.columns)
error = 0
for _, program in programs.iterrows():
    pg = program.to_dict()
    if pg["situação"] == "EM FUNCIONAMENTO":
        try:
            print("\n\n", f"[{_}] - ID")
            _type = list()
            for course in ast.literal_eval(pg["cursos"]):
                _course = normalize_keys(course)
                if _course["situacao"] == "EM FUNCIONAMENTO":
                    _type.append(_course["nivel"])
                print(_course["nota"])
                SCRIPT_SQL = """
                    INSERT INTO public.graduate_program(
                        code, name, area, modality, type, rating,
                        institution_id, state, city, region, url_image, acronym,
                        description, visible, site, created_at, updated_at)
                    VALUES (%(código)s, %(nome)s, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """
                SCRIPT_SQL = """
                    SELECT (%(código)s, %(nome)s, %(área de avaliação)s, '',
                        %(type)s)
                    """
            pg["type"] = "/".join(_type)
            # print(Connection().select(SCRIPT_SQL, pg))
        except Exception:
            error += 1
    else:
        error += 1

print(error)
