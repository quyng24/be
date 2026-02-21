from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_db
from app.crud import find_best_match
from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.schemas.attendance import AttendanceLogListResponse, AttendanceRequest

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in")
def check_attendance(data: AttendanceRequest, db: Session = Depends(get_db)):

    result = find_best_match(db, data.face_vector, threshold=0.95)

    if result is None:
        return {
            "status": 404,
            "message": "Không nhận diện được khuôn mặt. Vui lòng thử lại hoặc đăng ký mới!",
            "data": None
        }

    student, score = result

    today = date.today()
    last_log = db.query(AttendanceLog).filter(
        AttendanceLog.student_id == student.id,
        func.date(AttendanceLog.checkin_time) == today 
    ).first()

    if last_log:
        return {
            "status": 202,
            "message": f"Võ sinh {student.name} đã điểm danh hôm nay rồi.",
            "data": {"id": student.id, "name": student.name}
        }

    new_log = AttendanceLog(student_id=student.id)
    try:
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi lưu dữ liệu.")

    return {
        "status": 200,
        "message": f"Điểm danh thành công! Xin chào {student.name}",
        "data": {
            "id": student.id,
            "name": student.name,
            "similarity": float(score)
        }
    }


@router.get("/logs", response_model=AttendanceLogListResponse)
def get_attendance_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size

    query = db.query(AttendanceLog).join(Student)

    total = query.count()

    logs = (query.order_by(AttendanceLog.checkin_time.desc()).offset(skip).limit(page_size).all())

    data = [
        {
            "id": log.id,
            "student_id": log.student_id,
            "student_name": log.student.name,
            "checkin_time": log.checkin_time
        }
        for log in logs
    ]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": data
    }