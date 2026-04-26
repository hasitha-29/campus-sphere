import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_project.settings')
django.setup()

from backend_login_system.models import WeeklyTimetable

data = [
    ('Monday', 'Math', 'Physics', 'Chemistry', 'English', 'History'),
    ('Tuesday', 'Biology', 'Math', 'Physics', 'Computer', 'Art'),
    ('Wednesday', 'Chemistry', 'Biology', 'Math', 'Geography', 'PE'),
    ('Thursday', 'Physics', 'English', 'Computer', 'Math', 'History'),
    ('Friday', 'Art', 'Geography', 'PE', 'Biology', 'Chemistry')
]

if not WeeklyTimetable.objects.exists():
    for d, s1, s2, s3, s4, s5 in data:
        WeeklyTimetable.objects.create(
            day_of_week=d, slot_1=s1, slot_2=s2, slot_3=s3, slot_4=s4, slot_5=s5
        )
    print("Timetable populated.")
else:
    print("Timetable already exists.")
