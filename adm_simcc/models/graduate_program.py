from typing import Any, Optional

from pydantic import UUID4, BaseModel


class GraduateProgram(BaseModel):
    graduate_program_id: UUID4
    code: Optional[str]
    name: str
    name_en: Optional[str]
    basic_area: Optional[str]
    cooperation_project: Optional[str]
    area: str
    modality: str
    program_type: Optional[str]
    rating: Optional[str]
    institution_id: UUID4
    state: str = "BA"
    city: str = "Salvador"
    region: str = "Nordeste"
    url_image: Optional[str] = None
    acronym: Optional[str]
    description: Optional[str]
    visible: bool = False
    site: Optional[str] = None
    coordinator: Optional[str]
    email: Optional[str]
    start: Optional[Any]
    phone: Optional[str]
    periodicity: Optional[str]


class ListGraduateProgram(BaseModel):
    graduate_program_list: list[GraduateProgram]
