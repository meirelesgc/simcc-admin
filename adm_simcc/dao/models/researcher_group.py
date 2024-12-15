from pydantic import BaseModel, UUID4


class ResearcherGroup(BaseModel):
    nome_grupo: str
    nome_lider: str
    area: str
    ultimo_envio: str
    situacao: str
    institution_id: UUID4


class ListResearcherGroup(BaseModel):
    researcher_groups_list: list[ResearcherGroup]
