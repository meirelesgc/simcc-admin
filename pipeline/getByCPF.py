import pandas as pd
from zeep import Client
from sqlalchemy import create_engine, select, Table, MetaData

DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'  
DB_PORT = '5432'
DB_NAME = 'simcc_admin'

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
metadata = MetaData()
metadata.reflect(bind=engine)

researcher_table = metadata.tables['researcher']
institution_table = metadata.tables['institution']

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

with engine.connect() as conn:
    trans = conn.begin() 

    try:
        institution_query = select(institution_table)
        institution_result = conn.execute(institution_query).mappings().all()

        institution_map = {
            row['acronym'].strip().lower(): row['institution_id'] for row in institution_result
        }

        # Loop pelos dados do DataFrame
        for _, row in df.iterrows():
            try:
                name = row['NOME EMPR./CANDIDATO']
                cpf = row['NÚMERO DO CPF'].replace('.', '').replace('-', '')
                institution_acronym = row['EMPRESA'].strip().lower()

                id_lattes = get_lattes_id(cpf, name)
                print(f"Extraído: {id_lattes}")
            except Exception as e:
                print("Erro ao extrair dados:", e)
                continue

            id_institution = institution_map.get(institution_acronym)

            # Verifica se já existe no banco
            query = select(researcher_table).where(researcher_table.c.lattes_id == str(id_lattes))
            result = conn.execute(query).fetchone()

            if not result:
                insert_stmt = researcher_table.insert().values(
                    name=name.title(),
                    institution_id=id_institution,
                    lattes_id=id_lattes
                )
                conn.execute(insert_stmt)
                print(f"Inserido: {name.title()}")
            else:
                print(f"Já existe no banco: {name.title()}")

        trans.commit()  

    except Exception as e:
        print("Erro durante a transação:", e)
        trans.rollback()  
