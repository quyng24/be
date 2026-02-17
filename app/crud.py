from sqlalchemy.orm import Session
from .models import Student
from .utils import cosine_similarity
import numpy as np

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

def find_best_match(db: Session, new_vector, threshold=0.6):
    students=db.query(Student).all()
    if not students: return None
    
    best_score = -1
    best_student = None

    new_v = np.array(new_vector)

    for stu in students:
        stu_v = np.array(stu.face_vector) 
        score = cosine_similarity(new_v, stu_v)

        if score > best_score:
            best_score = score
            best_student = stu

    print(f"DEBUG: Best score found: {best_score} for {best_student.name if best_student else 'None'}")

    if best_student is None or best_score < threshold:
        return None

    return best_student, best_score