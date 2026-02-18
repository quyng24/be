from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import pytz

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

class Student(Base):
    __tablename__ = "students"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    birthday=Column(Date, nullable=False)
    face_vector=Column(ARRAY(Float), nullable=False)
    attendance_logs = relationship(
        "AttendanceLog",
        back_populates="student",
        cascade="all, delete"
    )

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Sử dụng timezone=True để lưu trữ thông tin múi giờ
    # server_default=func.now() vẫn ổn vì nó lưu UTC, ta sẽ convert khi SELECT
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendance_logs")