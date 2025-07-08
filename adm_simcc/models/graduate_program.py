from typing import Any, Optional

from pydantic import UUID4, BaseModel


class GraduateProgram(BaseModel):
    graduate_program_id: UUID4 = None
    code: Optional[str] = None
    name: str = None
    name_en: Optional[str] = None
    basic_area: Optional[str] = None
    cooperation_project: Optional[str] = None
    area: str = None
    modality: str = None
    type: Optional[str] = None
    rating: Optional[str] = None
    institution_id: UUID4
    state: str = "BA"
    city: str = "Salvador"
    region: str = "Nordeste"
    url_image: Optional[str] = None
    acronym: Optional[str] = None
    description: Optional[str] = None
    visible: bool = False
    site: Optional[str] = None
    coordinator: Optional[str] = None
    email: Optional[str] = None
    start: Optional[Any] = None
    phone: Optional[str] = None
    periodicity: Optional[str] = None
    menagers: Optional[list] = None


class ListGraduateProgram(BaseModel):
    graduate_program_list: list[GraduateProgram]
