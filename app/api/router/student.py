from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np

from app.api.deps import get_db
from app.crud import find_best_match
from app.models.student import Student
from app.schemas.student import StudentCreate

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/create")
def register_student(data: StudentCreate, db: Session = Depends(get_db)):
    vectors_array = np.array(data.face_vectors)
    if vectors_array.shape != (10, 128):
        raise HTTPException(
            status_code=400, 
            detail="Cần cung cấp đủ 10 mẫu khuôn mặt để đăng ký."
        )
    
    mean_vector = np.mean(vectors_array, axis=0).tolist()
    
    existing_match = find_best_match(db, np.array(mean_vector), threshold=0.95)

    if existing_match:
        student, score = existing_match
        return {
            "status": 409,
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