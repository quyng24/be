from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np

from app.api.deps import get_db
from app.crud import find_duplicate_student
from app.models.student import Student
from app.schemas.student import StudentCreate
from app.utils import normalize_vector, get_cosine_similarity

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/create")
def register_student(data: StudentCreate, db: Session = Depends(get_db)):
    vectors_array = np.array(data.face_vectors)

    if len(vectors_array) != 10 or vectors_array.shape[1] != 128:
        raise HTTPException(
            status_code=400,
            detail="Cần cung cấp đủ 10 mẫu khuôn mặt hợp lệ."
        )

    normalized_vectors = np.array([
        normalize_vector(v) for v in vectors_array
    ])

    temp_centroid = np.mean(normalized_vectors, axis=0)
    temp_centroid = normalize_vector(temp_centroid)

    filtered_vectors = [
        v for v in normalized_vectors
        if get_cosine_similarity(v, temp_centroid) > 0.9
    ]

    filtered_vectors = np.array(filtered_vectors)

    centroid = np.mean(filtered_vectors, axis=0)
    centroid = normalize_vector(centroid)

    existing_match = find_duplicate_student(
        db,
        centroid,
        threshold=0.95
    )

    if existing_match:
        student, score = existing_match
        return {
            "status": 409,
            "message": f"Khuôn mặt đã tồn tại ({score*100:.2f}%) - {student.name}"
        }

    new_student = Student(
        name=data.name,
        birthday=data.birthday,
        face_vector=centroid.tolist()
    )

    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi khi lưu dữ liệu.")

    return {
        "status": 201,
        "message": "+ 1 Võ sinh",
        "data": {
            "id": new_student.id,
            "name": new_student.name,
            "birthday": new_student.birthday
        }
    }
