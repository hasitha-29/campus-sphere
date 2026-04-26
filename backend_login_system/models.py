from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    # Role field specifically added for Admin/Student distinction
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} - {self.role}"

class Leave(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave Request by {self.student_name} - {self.status}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
    )
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=100)
    slot_time = models.CharField(max_length=50)
    otp = models.CharField(max_length=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.service_type} - {self.slot_time}"

class LostItem(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Matched', 'Matched'),
        ('Closed', 'Closed'),
    )
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    last_seen_place = models.CharField(max_length=150)
    date_lost = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

class FoundItem(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Matched', 'Matched'),
        ('Returned', 'Returned'),
    )
    finder = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    finder_name = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    found_place = models.CharField(max_length=150)
    date_found = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)

class RescheduleRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    old_slot_time = models.CharField(max_length=50)
    requested_slot_time = models.CharField(max_length=50)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Timetable(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Missed', 'Missed'),
        ('Rescheduled', 'Rescheduled'),
    )
    subject_name = models.CharField(max_length=150)
    class_date = models.DateField()
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    faculty_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

class Holiday(models.Model):
    holiday_date = models.DateField()
    holiday_name = models.CharField(max_length=150)

class RescheduledClass(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rescheduled', 'Rescheduled'),
    )
    subject_name = models.CharField(max_length=150)
    original_date = models.DateField()
    new_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

class Subject(models.Model):
    subject_name = models.CharField(max_length=150)
    faculty_name = models.CharField(max_length=150)
    weekly_hours = models.IntegerField(default=3)

class Room(models.Model):
    room_name = models.CharField(max_length=50)
    capacity = models.IntegerField(default=60)

class TimeSlot(models.Model):
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

class GeneratedTimetable(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty_name = models.CharField(max_length=150)
    room_name = models.CharField(max_length=50)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

class YearlySubject(models.Model):
    subject_name = models.CharField(max_length=150)
    total_required_classes = models.IntegerField(default=40)

class YearlyTimetable(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Holiday', 'Holiday'),
        ('Rescheduled', 'Rescheduled'),
    )
    subject = models.ForeignKey(YearlySubject, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=150)
    class_date = models.DateField()
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

class WeeklyTimetable(models.Model):
    day_of_week = models.CharField(max_length=20)
    slot_1 = models.CharField(max_length=100)
    slot_2 = models.CharField(max_length=100)
    slot_3 = models.CharField(max_length=100)
    slot_4 = models.CharField(max_length=100)
    slot_5 = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Holiday(models.Model):
    holiday_date = models.DateField(unique=True)
    holiday_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class CompensationSchedule(models.Model):
    original_class = models.CharField(max_length=100)
    missed_date = models.DateField()
    compensation_date = models.DateField()
    compensation_slot = models.CharField(max_length=20)
    status = models.CharField(max_length=50, default='Pending') # Pending, Approved
    created_at = models.DateTimeField(auto_now_add=True)
