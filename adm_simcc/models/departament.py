from pydantic import BaseModel, field_validator


class Professor(BaseModel):
    name: str
    ufmg_id: str
    responsibility: str


class Discipline(BaseModel):
    dep_id: str
    semester: str
    department: str
    academic_activity_code: str
    academic_activity_name: str
    academic_activity_ch: str
    demanding_courses: str
    oft: str
    id: str
    available_slots: str
    occupied_slots: str
    percent_occupied_slots: str
    schedule: str
    language: str
    professor: list[Professor]
    status: str

    @field_validator("professor", mode="before")
    def parse_professor(cls, value):
        professor = value.replace("\n", ",").replace(",,", ",").split(",")
        if len(professor) < 3:
            return [Professor(name="", ufmg_id="", responsibility="")]

        professors_list = list()
        for i in range(0, len(professor), 3):
            professors_list.append(
                Professor(
                    name=professor[i],
                    ufmg_id=professor[i + 1],
                    responsibility=professor[i + 2],
                )
            )
        return professors_list

    @field_validator("semester", mode="before")
    def parse_semester(cls, value):
        return value.replace("/", ".")


class ListDiscipline(BaseModel):
    list_discipline: list[Discipline]
