from pydantic import BaseModel
from typing import List
from datetime import date

class StudentCreate(BaseModel):
    name: str
    birthday: date
    face_vectors: List[List[float]]