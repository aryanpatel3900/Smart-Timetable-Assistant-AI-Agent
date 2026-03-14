from datetime import date

def days_until_exam(exam_date):
    today = date.today()
    delta = exam_date - today
    return delta.days

def get_study_plan(exam_name, exam_date, hours_per_day=2):
    days_left = days_until_exam(exam_date)
    if days_left <= 0:
        return f"❌ {exam_name} exam already passed!"
    
    total_hours = days_left * hours_per_day
    return {
        "exam": exam_name,
        "days_left": days_left,
        "total_study_hours": total_hours,
        "hours_per_day": hours_per_day,
        "suggestion": f"Study {hours_per_day} hrs/day for {days_left} days = {total_hours} total hours"
    }