from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Dict, List
from datetime import date, datetime
import pytz

class AttendanceRequest(BaseModel):
    face_vectors: List[List[float]]

class AttendanceLogResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    checkin_time: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('checkin_time')
    def convert_to_vn_time(self, dt: datetime):
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        
        return dt.astimezone(vn_tz).strftime('%Y-%m-%d %H:%M:%S')

class AttendanceLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[AttendanceLogResponse]

class WeeklyAttendanceRow(BaseModel):
    student_id: int
    name: str
    weeks: Dict[str, int]
    total_attended: int

class MonthlyAttendanceResponse(BaseModel):
    total_weeks: int
    data: List[WeeklyAttendanceRow]