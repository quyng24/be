from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.router.student import router as student_router
from app.api.router.attendance import router as attendance_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
api_router.include_router(student_router, prefix="/api/students", tags=["Students"])
api_router.include_router(attendance_router, prefix="/api", tags=["Attendance"])
