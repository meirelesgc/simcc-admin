import os

import pandas as pd
import psycopg2

from adm_simcc.dao import Connection

database = Connection()

dataframe = pd.read_excel('files/researcher.xlsx')

for _, data in dataframe.iterrows():
    print(data['Área_Lider'], data['Título'], data['CDT_FIEB'], data['URL_Lattes'], data['URL_ORCID'], data['E-mail CIMATEC'], data['E-mail Outro'], data['Foto'], data['Tipo de Item'], data['Caminho'])
    break