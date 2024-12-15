from pydantic import UUID4, BaseModel


class GraduateProgramStudent(BaseModel):
    student_id: UUID4
    name: str
    lattes_id: str
    institution_id: UUID4
    graduate_program_id: UUID4
    year: int


class ListGraduateProgramStudent(BaseModel):
    student_list: list[GraduateProgramStudent]
