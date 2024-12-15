from pydantic import BaseModel, field_validator, UUID4
from datetime import datetime


class Teacher(BaseModel):
    matric: str
    inscUFMG: str
    nome: str
    genero: str
    situacao: str
    rt: str
    clas: str
    cargo: str
    classe: str
    ref: str
    titulacao: str
    entradaNaUFMG: datetime
    progressao: datetime
    year_charge: str
    semester: str

    @field_validator("entradaNaUFMG", mode="before")
    def parse_entradaNaUFMG(cls, value):
        return datetime.strptime(value, "%d/%m/%Y")

    @field_validator("progressao", mode="before")
    def parse_progressao(cls, value):
        return datetime.strptime(value, "%d/%m/%Y")


class ListTeachers(BaseModel):
    list_teachers: list[Teacher]


class Role(BaseModel):
    role: str
    researcher_id: UUID4


class ListRole(BaseModel):
    list_roles: list[Role]
