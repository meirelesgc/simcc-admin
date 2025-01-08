import pandas as pd

from adm_simcc.dao import Connection

database = Connection()

dataframe = pd.read_excel("files/researcher.xlsx")

for _, data in dataframe.iterrows():
    SCRIPQ_SQL = """
    UPDATE researcher
    SET extra_field = %(extra_field)s
    WHERE lattes_id = %(lattes_id)s;
    """
    try:
        researcher = {
            "extra_field": data.get("Área_Lider").title().strip(),
            "institution_id": "083a16f0-cccf-47d2-a676-d10b8931f66a",
            "lattes_id": data.get("URL_Lattes", "")
            .strip()
            .split("/")[-1]
            .zfill(16),
            "name": data.get("Título").title().strip(),
        }
        database.exec(SCRIPQ_SQL, researcher)
    except Exception:
        print("Erro grave!!!!")
        print(data)
