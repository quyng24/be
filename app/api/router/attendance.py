from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import find_best_match
from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.schemas.attendance import AttendanceLogListResponse, AttendanceRequest

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/main")
def check_attendance(data: AttendanceRequest, db: Session = Depends(get_db)):

    result = find_best_match(db, data.face_vector, threshold=0.97)

    if result is None:
        raise HTTPException(status_code=404, detail="No match found")

    student, score = result

    time_threshold = datetime.utcnow() - timedelta(minutes=2)
    last_log = db.query(AttendanceLog).filter(
        AttendanceLog.student_id == student.id,
    ).first()

    if last_log:
        return {
            "status": 202,
            "message": "Điểm danh 1 lần thôi",
            "data": {"name": student.name, "already_logged": True}
        }
    

    new_log = AttendanceLog(student_id=student.id)
    db.add(new_log)
    db.commit()

    return {
        "status": 200,
        "message": "Điểm danh thành công! Xin chào",
        "data": {
            "id": student.id,
            "name": student.name,
            "similarity": score
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