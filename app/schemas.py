from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List
from datetime import date, datetime
import pytz

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

    # Cấu hình để làm việc với SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)

    @field_serializer('checkin_time')
    def convert_to_vn_time(self, dt: datetime):
        # Xác định múi giờ VN
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        
        # Nếu datetime chưa có thông tin múi giờ, coi nó là UTC
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
            
        # Chuyển sang giờ VN và format đẹp để FE không cần xử lý lại
        return dt.astimezone(vn_tz).strftime('%Y-%m-%d %H:%M:%S')

class AttendanceLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[AttendanceLogResponse]