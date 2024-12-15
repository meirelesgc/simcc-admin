from uuid import uuid4

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


if __name__ == "__main__":
    data = [
        {
            "graduate_program_id": uuid4(),
            "student_id": uuid4(),
            "name": "John Doe",
            "lattes_id": "!@#",
            "institution_id": uuid4(),
            "year": "2020; 2021; 2034",
        }
    ]

    student_list = ListGraduateProgramStudent(student_list=data)
    print(student_list.model_dump())
    print(student_list.student_list[0].model_dump())
