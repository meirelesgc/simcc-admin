import ast
import unicodedata
import json
import pandas as pd

from adm_simcc.dao import Connection


def normalize_string(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def normalize_keys(d):
    def normalize(s):
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.lower()

    return {normalize(k): v for k, v in d.items()}


def get_institution_id(institution):
    SCRIPT_SQL = """
        SELECT institution_id FROM institution WHERE name ILIKE %(institution)s
        """
    institution_id = Connection().select(
        SCRIPT_SQL, {"institution": institution}
    )
    if institution_id:
        return institution_id[0][0]
    return None


with open("files/city.json", "r", encoding="utf-8") as buffer:
    citys = json.load(buffer)

programs = pd.read_csv("files/programs.csv")

programs["ies_nome"] = programs["ies_nome"].where(
    programs["ies_nome"].notnull(), None
)
error = 0
for _, program in programs.iterrows():
    pg = program.to_dict()
    if pg["situação"] == "EM FUNCIONAMENTO":
        try:
            pg["city"], pg["state"] = pg["ies_municipio"].split(" - ")
            if institution_id := get_institution_id(pg["ies_nome"]):
                pg["institution_id"] = institution_id
            else:
                raise Exception

            _type = list()
            modality = set()
            for course in ast.literal_eval(pg["cursos"]):
                _course = normalize_keys(course)
                if _course["situacao"] == "EM FUNCIONAMENTO":
                    if "profissional" in normalize_string(
                        _course["nota"]
                    ) or "profissional" in normalize_string(_course["nivel"]):
                        modality.add(1)
                    else:
                        modality.add(0)
                    _type.append(_course["nivel"])

                if 0 in modality and 1 in modality:
                    pg["modality"] = "ACADÊMICO/PROFISSIONAL"
                elif 0 in modality:
                    pg["modality"] = "PROFISSIONAL"
                if 1 in modality:
                    pg["modality"] = "ACADÊMICO"

                SCRIPT_SQL = """
                    INSERT INTO public.graduate_program (
                        code, name, area, modality, type,
                        institution_id, state, city, visible, site
                    ) VALUES (
                        %(código)s, %(nome)s, %(área de avaliação)s,
                        %(modality)s, %(type)s, %(institution_id)s,
                        %(state)s, %(city)s, TRUE, %(ies_url)s
                    )
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        area = EXCLUDED.area,
                        modality = EXCLUDED.modality,
                        type = EXCLUDED.type,
                        institution_id = EXCLUDED.institution_id,
                        state = EXCLUDED.state,
                        city = EXCLUDED.city,
                        site = EXCLUDED.site,
                        visible = TRUE;
                    """
            pg["type"] = "/".join(_type)

            Connection().exec(SCRIPT_SQL, pg)
        except Exception:
            error += 1
    else:
        error += 1

SCRIPT_SQL = """
    UPDATE graduate_program SET
        name = INITCAP(name),
        area = UPPER(area)
    """
Connection().exec(SCRIPT_SQL)
