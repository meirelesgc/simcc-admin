import pandas as pd
from zeep import Client
from sqlalchemy import create_engine, select, Table, MetaData


DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'  
DB_PORT = '5432'
DB_NAME = 'simcc'

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

metadata = MetaData()
metadata.reflect(bind=engine)
researcher_table = metadata.tables['researcher']

instituition = [
    {'name': 'UEFS', 'id': '083a16f0-cccf-47d2-a676-d10b8931f66b'},
    {'name': 'Universidade Do Estado Da Bahia', 'id': '3215039c-57a3-4325-a578-ccf001a83864'},
    {'name': 'Universidade Federal Da Bahia', 'id': '34baec39-a219-4d8f-9c8e-40a158bffa00'},
]

# Função para obter o ID Lattes via CPF
def get_lattes_id(cpf, nome, data_nascimento=None):

    client = Client("http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl")

    try:
        result = client.service.getIdentificadorCNPq(
            cpf=cpf,
            nomeCompleto=nome,
            dataNascimento=data_nascimento or ''
        )
        return result
    except Exception as e:
        print(f"Erro ao buscar ID para {nome}: {e}")
        return None


df = pd.read_excel('MPUBA25.03.2025.xlsx')

# Loop pelos dados
with engine.connect() as conn:
    for _, row in df.iterrows():
        try:
            name = row['NOME EMPR./CANDIDATO']
            cpf = row['NÚMERO DO CPF'].replace('.', '').replace('-', '')
            instituition_name = row['EMPRESA']

            instituition_info = next((e for e in instituition if e['name'].strip().lower() == instituition_name.strip().lower()), None)

            id_lattes = get_lattes_id(cpf, name)
            print(f"Extraído: {id_lattes}")
        except Exception as e:
            print("Erro ao extrair dados:", e)
            continue

        # Continua apenas se empresa_info existir e id_lattes for inteiro
        if instituition_info and isinstance(id_lattes, int):
            id_instituition= instituition_info['id']

            query = select(researcher_table).where(researcher_table.c.lattes_id == str(id_lattes))
            result = conn.execute(query).fetchone()
            print(result)
            if not result:
                insert_stmt = researcher_table.insert().values(
                    name=name.title(),
                    institution_id=id_instituition,
                    lattes_id=id_lattes
                )
                conn.execute(insert_stmt)
                print(f"Inserido: {name.title()}")
            else:
                print(f"Já existe no banco: {name.title()}")
        else:
            print(f"Dados inválidos para {name}: empresa_info={instituition_info}, id_lattes={id_lattes}")

