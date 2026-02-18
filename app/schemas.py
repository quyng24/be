from pydantic import BaseModel
from typing import List
from datetime import date, datetime

class StudentCreate(BaseModel):
    name: str
    birthday: date
    face_vector: List[List[float]]

class AttendanceRequest(BaseModel):
    face_vector: List[float]

class AttendanceLogResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    checkin_time: datetime

class AttendanceLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[AttendanceLogResponse]