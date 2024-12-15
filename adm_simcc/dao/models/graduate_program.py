from typing import Optional
from pydantic import UUID4, BaseModel


class GraduateProgram(BaseModel):
    graduate_program_id: UUID4
    code: Optional[str]
    name: str
    area: str
    modality: str
    type: Optional[str]
    rating: Optional[str]
    institution_id: UUID4
    city: str = "Salvador"
    url_image: Optional[str]
    acronym: Optional[str] = None
    description: Optional[str]
    visible: bool = False


class ListGraduateProgram(BaseModel):
    graduate_program_list: list[GraduateProgram]
