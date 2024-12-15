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
        professor = value.replace('\n', ',').replace(',,', ',').split(',')
        if len(professor) < 3:
            return [Professor(name='', ufmg_id='', responsibility='')]

        professors_list = list()
        for i in range(0, len(professor), 3):
            professors_list.append(Professor(
                name=professor[i],
                ufmg_id=professor[i+1],
                responsibility=professor[i+2]))
        return professors_list

    @field_validator('semester', mode='before')
    def parse_semester(cls, value):
        return value.replace('/', '.')


class ListDiscipline(BaseModel):
    list_discipline: list[Discipline]


if __name__ == "__main__":
    data = [
        {
            "semester": "2023/2",
            "department": "Computer Science",
            "academic_activity_code": "CS101",
            "academic_activity_name": "Introduction to Programming",
            "academic_activity_ch": "60",
            "demanding_courses": "Computer Science, Information Systems",
            "oft": "OFT1",
            "id": "001",
            "available_slots": "30",
            "occupied_slots": "28",
            "percent_occupied_slots": "93.33",
            "schedule": "Mon-Wed 10:00-12:00",
            "language": "English",
            "professor": "RENAN FERNANDES KOZAN, 300276, 60",
            "status": "Active",
        }
    ]

    courses = [Discipline(**item) for item in data]

    for course in courses:
        print(course)
