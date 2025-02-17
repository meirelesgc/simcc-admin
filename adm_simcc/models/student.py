from pydantic import UUID4, BaseModel, field_validator


class GraduateProgramStudent(BaseModel):
    student_id: UUID4 = None
    name: str = None
    lattes_id: str
    institution_id: UUID4 = None
    graduate_program_id: UUID4
    year: list[int]

    @field_validator("year", mode="before")
    def split_year(cls, v):
        return [int(year.strip()) for year in v.split(";")]


class ListGraduateProgramStudent(BaseModel):
    student_list: list[GraduateProgramStudent]
