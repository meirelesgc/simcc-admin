from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, field_validator


class GraduateProgramResearcher(BaseModel):
    graduate_program_id: UUID4
    researcher_id: Optional[UUID4] = None
    year: list
    type_: str
    lattes_id: Optional[str] = None

    @field_validator("year", mode="before")
    def split_year(cls, v):
        return [int(year.strip()) for year in v.split(";")]


class ListResearcher(BaseModel):
    researcher_list: list[GraduateProgramResearcher]


if __name__ == "__main__":
    data = [
        {
            "graduate_program_id": uuid4(),
            "researcher_id": uuid4(),
            "year": "2020; 2021; 2034",
            "type_": "COLABORADOR",
            "lattes_id": "!@#",
        }
    ]

    lista = ListResearcher(researcher_list=data)
