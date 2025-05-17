from datetime import datetime

from pydantic import UUID4, BaseModel, field_validator


class Technician(BaseModel):
    matric: str
    insUFMG: str
    nome: str
    genero: str
    denoSit: str
    rt: str
    classe: str
    cargo: str
    nivel: str
    ref: str
    titulacao: str
    setor: str
    detalheSetor: str
    dtIngOrg: datetime
    dataProg: datetime
    year_charge: str
    semester: str

    @field_validator("dtIngOrg", mode="before")
    def parse_dtIngOrg(cls, value):
        return datetime.strptime(value, "%d/%m/%Y")

    @field_validator("dataProg", mode="before")
    def parse_dataProg(cls, value):
        return datetime.strptime(value, "%d/%m/%Y")


class ListTechnician(BaseModel):
    list_technician: list[Technician]


class Role(BaseModel):
    role: str
    researcher_id: UUID4


class ListRole(BaseModel):
    list_roles: list[Role]


class TechnicianDepartament(BaseModel):
    dep_id: int
    Technician_id: UUID4


class ListTechnicianDepartament(BaseModel):
    technician_departament: list[TechnicianDepartament]
