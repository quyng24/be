from collections import defaultdict
from sqlalchemy.orm import Session
from datetime import date
import calendar

from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.utils import get_week_of_moth



def get_monthly_attendance(db: Session, month: int, year: int):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    logs = db.query(AttendanceLog).filter(
        AttendanceLog.checkin_time >= start_date,
        AttendanceLog.checkin_time < end_date
    ).all()

    attendance_map = defaultdict(lambda: defaultdict(int))

    for log in logs:
        week = get_week_of_moth(log.checkin_time.date())
        attendance_map[log.student_id][week] += 1

    students = db.query(Student).all()

    num_days = calendar.monthrange(year, month)[1]
    total_week = (num_days - 1) // 7 + 1

    result = []

    for stu in students:
        week_data = {}
        total_attended = 0

        for week in range(1, total_week + 1):
            count = attendance_map[stu.id].get(week, 0)
            week_data[f"week_{week}"] = count
            total_attended += count

        result.append({
            "student_id": stu.id,
            "name": stu.name,
            "weeks": week_data,
            "total_attended": total_attended
        })

    return {
        "total_weeks": total_week,
        "data": result
    }
