from sqlalchemy.orm import Session
from .models import Student
from .utils import cosine_similarity

THRESHOLD=0.6

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

def find_best_match(db: Session, face_vector):
    students=db.query(Student).all()
    best_student=None
    best_score=0

    for stu in students:
        score=cosine_similarity(face_vector, stu.face_vector)
        if score>best_score:
            best_score=score
            best_student=stu

    if best_score <THRESHOLD:
        return None
    
    if best_student is None:
        return None
    return best_student, best_score