from pydantic import UUID4, BaseModel


class Researcher(BaseModel):
    researcher_id: UUID4
    name: str
    lattes_id: str
    institution_id: UUID4


class ListResearchers(BaseModel):
    researcher_list: list[Researcher]


class ResearcherDepartament(BaseModel):
    dep_id: int
    researcher_id: UUID4


class ListResearcherDepartament(BaseModel):
    researcher_departament: list[ResearcherDepartament]
