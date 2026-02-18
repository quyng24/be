from sqlalchemy.orm import Session
from .models import Student
from .utils import cosine_similarity, get_cosine_similarity
import numpy as np
from typing import List, Tuple, Optional

def create_student(db: Session, data):
    student=Student(
        name=data.name,
        birthday=data.birthday,
        face_vector=data.face_vector
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def find_best_match(db: Session, new_vector: np.ndarray, threshold=0.6) -> Optional[Tuple[Student, float]]:
    students = db.query(Student).all()
    if not students: return None
    
    best_score = -1
    best_student = None

    for stu in students:
        stu_v = np.array(stu.face_vector) 
        # So sánh vector mới với vector đại diện trong DB
        score = get_cosine_similarity(new_vector, stu_v)

        if score > best_score:
            best_score = score
            best_student = stu

    if best_student is None or best_score < threshold:
        return None

    return best_student, best_score