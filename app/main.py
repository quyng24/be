import numpy as np
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import Base, engine, SessionLocal
from .schemas import StudentCreate, AttendanceRequest, AttendanceLogListResponse
from .crud import find_best_match, create_student
from .models import AttendanceLog, Student

app= FastAPI()

origins = [
    "http://localhost:3000",
    "https://panda-taekwondo.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/students/create")
def register_student(data: StudentCreate, db: Session = Depends(get_db)):
    vectors_array = np.array(data.face_vector)
    if vectors_array.shape != (5, 128):
        raise HTTPException(
            status_code=400, 
            detail="Cần cung cấp đủ 5 mẫu khuôn mặt để đăng ký."
        )
    
    mean_vector = np.mean(vectors_array, axis=0).tolist()
    
    existing_match = find_best_match(db, np.array(mean_vector), threshold=0.97)

    if existing_match:
        student, score = existing_match
        return {
            "status": 400,
            "message": f"Khuôn mặt này đã được đăng ký (Khớp {score*100:.2f}%) cho võ sinh: {student.name}",
        }
    
    new_student = Student(
        name=data.name,
        birthday=data.birthday,
        face_vector=mean_vector
    )
    
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi khi lưu dữ liệu vào cơ sở dữ liệu.")

    return {
        "status": 201,
        "message": "+ 1 Võ sinh",
        "data": {
            "id": new_student.id,
            "name": new_student.name,
            "birthday": new_student.birthday
        }
    }

@app.post("/students/attendance")
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

@app.get("/students/attendance/logs", response_model=AttendanceLogListResponse)
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