import pandas as pd
from zeep import Client

columns = ["aconym", "name", "CPF"]
client = Client("http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl")
dataframe = pd.read_csv("pesquisadores.CSV", sep=";")

for _, data in dataframe.iterrows():
    try:
        cpf = data.get("cpf").replace(".", "").replace("-", "")
        response = client.service.getIdentificadorCNPq(
            cpf=cpf, nomeCompleto="", dataNascimento=""
        )
        if response:
            data.lattes_id = response
    except Exception:
        print(f"Erro identificado no registro {_}")
