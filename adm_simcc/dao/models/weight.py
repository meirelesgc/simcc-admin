from pydantic import UUID4, BaseModel


class Weights(BaseModel):
    institution_id: UUID4
    A1: float
    A2: float
    A3: float
    A4: float
    B1: float
    B2: float
    B3: float
    B4: float
    C: float
    SQ: float
    BOOK: float
    BOOK_CHAPTER: float
    SOFTWARE: str
    PATENT_GRANTED: str
    PATENT_NOT_GRANTED: str
    REPORT: str
    F1: float = 0
    F2: float = 0
    F3: float = 0
    F4: float = 0
    F5: float = 0
