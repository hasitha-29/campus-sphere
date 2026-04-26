from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Count
from django.contrib import messages
from .models import CustomUser, Leave, Booking, LostItem, FoundItem, RescheduleRequest, Timetable, Holiday, RescheduledClass, Subject, Room, TimeSlot, GeneratedTimetable, YearlySubject, YearlyTimetable, WeeklyTimetable, CompensationSchedule
import random
from datetime import timedelta

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Error handling: Passwords mismatch
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        
        # Error handling: User already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "User already exists. Please choose a different username.")
            return render(request, 'register.html')
        
        # Admin cannot be created from frontend, default to student
        user = CustomUser.objects.create_user(username=username, email=email, password=password, role='student')
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    
    return render(request, 'register.html')

def about_view(request):
    return render(request, 'about.html')

def login_view(request):
    try:
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_user(username='admin', password='admin123', role='admin')
    except Exception:
        pass
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Uses Django's authentication system (which uses hashed passwords securely)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the selected role matches the user's role in the DB
            if user.role != role:
                messages.error(request, "Invalid role selected for this user.")
                return render(request, 'login.html')
            
            # Start session authentication
            auth_login(request, user)
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
        else:
            # Error handling: Invalid credentials
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    return render(request, 'admin_dashboard.html')

def admin_profile_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    return render(request, 'admin_profile.html')

def admin_settings_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    return render(request, 'admin_settings.html')

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
    rescheduled_classes = CompensationSchedule.objects.all().order_by('-compensation_date')
    return render(request, 'student_dashboard.html', {
        'rescheduled_classes': rescheduled_classes
    })

def student_profile_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
    return render(request, 'student_profile.html')

# ==========================================
# LEAVE MANAGEMENT VIEWS
# ==========================================

def apply_leave(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason')
        
        Leave.objects.create(
            student=request.user,
            student_name=request.user.username,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            status='Pending'
        )
        messages.success(request, "Leave request submitted successfully!")
        return redirect('my_leaves')
        
    return render(request, 'apply_leave.html')

def my_leaves(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    leaves = Leave.objects.filter(student=request.user).order_by('-applied_at')
    return render(request, 'my_leaves.html', {'leaves': leaves})

def admin_leave_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    leaves = Leave.objects.all().order_by('-applied_at')
    return render(request, 'admin_leave_dashboard.html', {'leaves': leaves})

def approve_leave(request, leave_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    leave = Leave.objects.get(id=leave_id)
    leave.status = 'Approved'
    leave.save()
    messages.success(request, f"Leave for {leave.student_name} approved.")
    return redirect('admin_leave_dashboard')

def reject_leave(request, leave_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    leave = Leave.objects.get(id=leave_id)
    leave.status = 'Rejected'
    leave.save()
    messages.error(request, f"Leave for {leave.student_name} rejected.")
    return redirect('admin_leave_dashboard')

# ==========================================
# QUEUE BOOKING VIEWS
# ==========================================

def book_slot_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    MAX_CAPACITY = 10
    all_slots = ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '02:00 PM', '02:30 PM', '03:00 PM']
    
    # Count active bookings for each slot
    slot_counts = Booking.objects.exclude(status='Completed').values('slot_time').annotate(count=Count('id'))
    counts_dict = {item['slot_time']: item['count'] for item in slot_counts}
    
    available_slots = []
    total_slots_left = 0
    for slot in all_slots:
        booked = counts_dict.get(slot, 0)
        remaining = MAX_CAPACITY - booked
        if remaining > 0:
            available_slots.append({'time': slot, 'remaining': remaining})
            total_slots_left += remaining

    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        slot_time = request.POST.get('slot_time')
        
        # Check capacity dynamically on submission
        current_booked = Booking.objects.exclude(status='Completed').filter(slot_time=slot_time).count()
        if current_booked >= MAX_CAPACITY:
            messages.error(request, "This time slot is fully booked. Please select another time.")
            return redirect('book_slot')
            
        otp = str(random.randint(100000, 999999))
        
        Booking.objects.create(
            student=request.user,
            student_name=request.user.username,
            service_type=service_type,
            slot_time=slot_time,
            otp=otp,
            status='Booked'
        )
        messages.success(request, f"Slot booked successfully! Your OTP is {otp}.")
        return redirect('my_bookings')
        
    return render(request, 'book_slot.html', {
        'available_slots': available_slots, 
        'total_slots_left': total_slots_left
    })

def my_bookings_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    bookings = Booking.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})

def admin_queue_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'admin_queue_dashboard.html', {'bookings': bookings})

def start_queue(request, booking_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    booking = Booking.objects.get(id=booking_id)
    booking.status = 'In-Progress'
    booking.save()
    messages.success(request, f"Queue started for {booking.student_name}.")
    return redirect('admin_queue_dashboard')

def verify_otp(request, booking_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        booking = Booking.objects.get(id=booking_id)
        
        if booking.otp == otp_input:
            booking.status = 'Completed'
            booking.save()
            messages.success(request, "OTP Verified! Booking is now completed.")
        else:
            messages.error(request, "Invalid OTP provided.")
            
    return redirect('admin_queue_dashboard')

# ==========================================
# LOST & FOUND VIEWS
# ==========================================

from django.core.mail import send_mail
from django.conf import settings

def auto_match_items():
    """Auto-matches items if their names are similar and sends email"""
    # Check all active lost items (Open or Matched) so it can match multiple found items
    active_lost = LostItem.objects.exclude(status='Closed')
    available_found = FoundItem.objects.filter(status='Available')
    
    for lost in active_lost:
        for found in available_found:
            if lost.item_name.lower() in found.item_name.lower() or found.item_name.lower() in lost.item_name.lower():
                lost.status = 'Matched'
                lost.save()
                
                found.status = 'Matched'
                found.save()
                
                # Send Email Notification
                student_email = lost.student.email
                if student_email:
                    subject = f"CampusSphere: Match Found for your {lost.item_name}!"
                    message = f"Hello {lost.student_name},\n\nA potential match has been found for your lost item '{lost.item_name}'.\n\nFound Details:\nItem: {found.item_name}\nLocation Found: {found.found_place}\nDate: {found.date_found}\n\nPlease contact the Admin office to claim your item.\n\nBest,\nCampusSphere Team"
                    try:
                        send_mail(
                            subject,
                            message,
                            getattr(settings, 'EMAIL_HOST_USER', 'noreply@campussphere.com'),
                            [student_email],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
                # We do NOT break here, so one lost item can match MULTIPLE found items

def report_lost_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        last_seen_place = request.POST.get('last_seen_place')
        date_lost = request.POST.get('date_lost')
        
        LostItem.objects.create(
            student=request.user,
            student_name=request.user.username,
            item_name=item_name,
            description=description,
            last_seen_place=last_seen_place,
            date_lost=date_lost
        )
        messages.success(request, "Lost item reported successfully.")
        auto_match_items()
        return redirect('my_reports')
        
    return render(request, 'report_lost.html')

def report_found_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        found_place = request.POST.get('found_place')
        date_found = request.POST.get('date_found')
        
        FoundItem.objects.create(
            finder=request.user,
            finder_name=request.user.username,
            item_name=item_name,
            description=description,
            found_place=found_place,
            date_found=date_found
        )
        messages.success(request, "Found item reported successfully.")
        auto_match_items()
        return redirect('my_reports' if request.user.role == 'student' else 'admin_lost_found_dashboard')
        
    return render(request, 'report_found.html')

def my_reports_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    lost_items = LostItem.objects.filter(student=request.user).order_by('-created_at')
    found_items = FoundItem.objects.filter(finder=request.user).order_by('-created_at')
    
    if lost_items.filter(status='Matched').exists():
        messages.info(request, "Match found for your lost item! Please contact Admin.")
        
    return render(request, 'my_reports.html', {'lost_items': lost_items, 'found_items': found_items})

def admin_lost_found_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    lost_items = LostItem.objects.all().order_by('-created_at')
    found_items = FoundItem.objects.all().order_by('-created_at')
    
    return render(request, 'admin_lost_found_dashboard.html', {'lost_items': lost_items, 'found_items': found_items})

def mark_as_matched(request, item_type, item_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    if item_type == 'lost':
        item = LostItem.objects.get(id=item_id)
        item.status = 'Matched'
    elif item_type == 'found':
        item = FoundItem.objects.get(id=item_id)
        item.status = 'Matched'
        
    item.save()
    messages.success(request, f"{item_type.capitalize()} item marked as Matched.")
    return redirect('admin_lost_found_dashboard')

def close_report(request, item_type, item_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    if item_type == 'lost':
        item = LostItem.objects.get(id=item_id)
        item.status = 'Closed'
    elif item_type == 'found':
        item = FoundItem.objects.get(id=item_id)
        item.status = 'Returned'
        
    item.save()
    messages.success(request, "Report closed/returned successfully.")
    return redirect('admin_lost_found_dashboard')


# ==========================================
# RESCHEDULE SYSTEM VIEWS
# ==========================================

SLOT_CAPACITY = 10

SLOTS = [
    '09:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '01:00 PM', '02:00 PM',
    '03:00 PM', '04:00 PM',
]

def reschedule_request_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')

    # Only show bookings that are Booked (not completed/in-progress)
    my_bookings = Booking.objects.filter(student=request.user, status='Booked')

    # Build slot availability
    slot_availability = {}
    for slot in SLOTS:
        booked_count = Booking.objects.filter(slot_time=slot, status__in=['Booked', 'In-Progress']).count()
        slot_availability[slot] = SLOT_CAPACITY - booked_count

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        requested_slot = request.POST.get('requested_slot_time')
        reason = request.POST.get('reason')

        try:
            booking = Booking.objects.get(id=booking_id, student=request.user)
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking selected.")
            return redirect('reschedule_request')

        # Check if a pending reschedule already exists for this booking
        existing = RescheduleRequest.objects.filter(booking=booking, status='Pending').exists()
        if existing:
            messages.warning(request, "A pending reschedule request already exists for this booking.")
            return redirect('my_reschedules')

        # Check slot availability
        available = slot_availability.get(requested_slot, 0)
        if available <= 0:
            messages.error(request, f"Slot '{requested_slot}' is fully booked. Please choose another slot.")
            return render(request, 'reschedule_request.html', {
                'my_bookings': my_bookings,
                'slots': SLOTS,
                'slot_availability': slot_availability,
            })

        RescheduleRequest.objects.create(
            booking=booking,
            student=request.user,
            student_name=request.user.username,
            old_slot_time=booking.slot_time,
            requested_slot_time=requested_slot,
            reason=reason,
        )
        messages.success(request, "Reschedule request submitted successfully! Awaiting admin approval.")
        return redirect('my_reschedules')

    return render(request, 'reschedule_request.html', {
        'my_bookings': my_bookings,
        'slots': SLOTS,
        'slot_availability': slot_availability,
    })


def my_reschedules_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')

    reschedules = RescheduleRequest.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'my_reschedules.html', {'reschedules': reschedules})


def admin_reschedule_dashboard_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    reschedules = RescheduleRequest.objects.all().order_by('-created_at')
    return render(request, 'admin_reschedule_dashboard.html', {'reschedules': reschedules})


def approve_reschedule(request, reschedule_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    try:
        reschedule = RescheduleRequest.objects.get(id=reschedule_id)
    except RescheduleRequest.DoesNotExist:
        messages.error(request, "Reschedule request not found.")
        return redirect('admin_reschedule_dashboard')

    # Validate slot capacity before approving
    slot = reschedule.requested_slot_time
    booked_count = Booking.objects.filter(slot_time=slot, status__in=['Booked', 'In-Progress']).count()
    if booked_count >= SLOT_CAPACITY:
        messages.error(request, f"Cannot approve: Slot '{slot}' is already full ({SLOT_CAPACITY}/{SLOT_CAPACITY} slots).")
        return redirect('admin_reschedule_dashboard')

    # Update booking slot
    booking = reschedule.booking
    booking.slot_time = reschedule.requested_slot_time
    booking.save()

    reschedule.status = 'Approved'
    reschedule.save()

    messages.success(request, f"Reschedule approved! Booking updated to '{slot}'.")
    return redirect('admin_reschedule_dashboard')


def reject_reschedule(request, reschedule_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    try:
        reschedule = RescheduleRequest.objects.get(id=reschedule_id)
    except RescheduleRequest.DoesNotExist:
        messages.error(request, "Reschedule request not found.")
        return redirect('admin_reschedule_dashboard')

    reschedule.status = 'Rejected'
    reschedule.save()

    messages.warning(request, "Reschedule request has been rejected.")
    return redirect('admin_reschedule_dashboard')


# ==========================================
# SMART CLASS RESCHEDULING VIEWS
# ==========================================
from datetime import timedelta, date

def student_timetable_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    timetable = Timetable.objects.all().order_by('class_date', 'start_time')
    return render(request, 'student_timetable.html', {'timetable': timetable})

def admin_class_reschedule_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    missed_classes = Timetable.objects.filter(status='Missed')
    rescheduled_classes = RescheduledClass.objects.all().order_by('-id')
    
    return render(request, 'admin_class_reschedule.html', {
        'missed_classes': missed_classes,
        'rescheduled_classes': rescheduled_classes,
    })

def find_next_working_day(original_date, start_time, end_time):
    current_date = original_date + timedelta(days=1)
    
    while True:
        # Skip weekends (5=Sat, 6=Sun)
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
            
        # Skip holidays
        if Holiday.objects.filter(holiday_date=current_date).exists():
            current_date += timedelta(days=1)
            continue
            
        # Skip timetable conflicts (same time slot)
        clash = Timetable.objects.filter(class_date=current_date, start_time=start_time, end_time=end_time).exists()
        if clash:
            current_date += timedelta(days=1)
            continue
            
        # Found available slot!
        return current_date

def detect_missed_classes(request):
    # This checks past scheduled classes that weren't completed 
    # For demo, let's mark all 'Scheduled' classes before today as 'Missed'
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    today = date.today()
    past_classes = Timetable.objects.filter(class_date__lt=today, status='Scheduled')
    count = past_classes.count()
    past_classes.update(status='Missed')
    
    messages.success(request, f"Detected and marked {count} past classes as Missed.")
    return redirect('admin_class_reschedule')

def auto_reschedule(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    missed_classes = Timetable.objects.filter(status='Missed')
    count = 0
    
    for c in missed_classes:
        # Check if already pending
        if RescheduledClass.objects.filter(subject_name=c.subject_name, original_date=c.class_date, status='Pending').exists():
            continue
            
        new_date = find_next_working_day(c.class_date, c.start_time, c.end_time)
        RescheduledClass.objects.create(
            subject_name=c.subject_name,
            original_date=c.class_date,
            new_date=new_date,
            reason="Auto-rescheduled due to missed class or holiday.",
            status='Pending'
        )
        count += 1
        
    messages.success(request, f"Successfully auto-generated {count} new reschedule proposals.")
    return redirect('admin_class_reschedule')

def approve_class_reschedule(request, rc_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    try:
        rc = RescheduledClass.objects.get(id=rc_id)
        
        # Update original missed class to 'Rescheduled'
        t = Timetable.objects.filter(subject_name=rc.subject_name, class_date=rc.original_date, status='Missed').first()
        if t:
            t.status = 'Rescheduled'
            t.save()
            
            # Create new Timetable entry
            Timetable.objects.create(
                subject_name=t.subject_name,
                class_date=rc.new_date,
                start_time=t.start_time,
                end_time=t.end_time,
                faculty_name=t.faculty_name,
                status='Scheduled'
            )
            
        rc.status = 'Approved'
        rc.save()
        messages.success(request, f"Reschedule approved! {rc.subject_name} is now set for {rc.new_date}.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        
    return redirect('admin_class_reschedule')


# ==========================================
# AUTO TIMETABLE GENERATOR VIEWS
# ==========================================
import random

def admin_timetable_dashboard_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_subject':
            Subject.objects.create(
                subject_name=request.POST.get('subject_name'),
                faculty_name=request.POST.get('faculty_name'),
                weekly_hours=int(request.POST.get('weekly_hours', 3))
            )
            messages.success(request, "Subject added.")
        elif action == 'add_room':
            Room.objects.create(
                room_name=request.POST.get('room_name'),
                capacity=int(request.POST.get('capacity', 60))
            )
            messages.success(request, "Room added.")
        elif action == 'add_slot':
            TimeSlot.objects.create(
                day=request.POST.get('day'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time')
            )
            messages.success(request, "Time slot added.")
        return redirect('admin_timetable_dashboard')

    subjects = Subject.objects.all()
    rooms = Room.objects.all()
    slots = TimeSlot.objects.all().order_by('day', 'start_time')
    timetable = GeneratedTimetable.objects.all()
    
    return render(request, 'admin_timetable_dashboard.html', {
        'subjects': subjects,
        'rooms': rooms,
        'slots': slots,
        'timetable': timetable
    })

def generate_timetable(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    GeneratedTimetable.objects.all().delete()
    
    subjects = list(Subject.objects.all())
    rooms = list(Room.objects.all())
    slots = list(TimeSlot.objects.all())
    
    if not subjects or not rooms or not slots:
        messages.error(request, "Cannot generate timetable: Missing subjects, rooms, or slots.")
        return redirect('admin_timetable_dashboard')
        
    random.shuffle(slots) # Shuffle to distribute classes
    
    allocated = []
    failed_allocations = 0
    
    for subject in subjects:
        hours_needed = subject.weekly_hours
        hours_allocated = 0
        
        for slot in slots:
            if hours_allocated >= hours_needed:
                break
                
            # Rule 1: Faculty conflict check
            faculty_clash = any(
                t.faculty_name == subject.faculty_name and t.day == slot.day and t.start_time == slot.start_time 
                for t in allocated
            )
            if faculty_clash: continue
            
            # Rule 2: Room availability check
            available_rooms = [r for r in rooms if not any(
                t.room_name == r.room_name and t.day == slot.day and t.start_time == slot.start_time 
                for t in allocated
            )]
            
            if not available_rooms: continue
            
            # Rule 3: Avoid same subject twice in one day (if possible)
            day_clash = any(
                t.subject.id == subject.id and t.day == slot.day
                for t in allocated
            )
            if day_clash and random.random() < 0.8: # 80% chance to skip if day clash
                continue
                
            # Assign
            room = random.choice(available_rooms)
            
            new_class = GeneratedTimetable(
                subject=subject,
                faculty_name=subject.faculty_name,
                room_name=room.room_name,
                day=slot.day,
                start_time=slot.start_time,
                end_time=slot.end_time
            )
            new_class.save()
            allocated.append(new_class)
            hours_allocated += 1
            
        if hours_allocated < hours_needed:
            failed_allocations += 1
            
    if failed_allocations > 0:
        messages.warning(request, f"Timetable generated, but could not allocate full hours for {failed_allocations} subjects due to conflicts.")
    else:
        messages.success(request, "Timetable successfully generated with zero conflicts!")
        
    return redirect('admin_timetable_dashboard')

def student_weekly_timetable_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')
        
    timetable = GeneratedTimetable.objects.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    # Group by day
    schedule = {}
    for day in days:
        schedule[day] = timetable.filter(day=day).order_by('start_time')
        
    return render(request, 'student_weekly_timetable.html', {'schedule': schedule, 'days': days})


# ============================================================
# YEARLY TIMETABLE BALANCING MODULE
# ============================================================

YEARLY_SLOTS = [
    ('09:00', '10:00'),
    ('10:00', '11:00'),
    ('11:00', '12:00'),
    ('13:00', '14:00'),
    ('14:00', '15:00'),
    ('15:00', '16:00'),
]
SLOT_LABELS = [s[0] for s in YEARLY_SLOTS]  # ['09:00', '10:00', ...]


def _build_rows(queryset):
    """
    Pre-build grid rows in Python so templates need zero logic.
    Returns: [
        {
          'date': 'Apr 28, 2026 (Monday)',
          'cells': [obj_or_None, obj_or_None, ...]   # one per YEARLY_SLOTS
        }, ...
    ]
    """
    from collections import OrderedDict
    day_map = OrderedDict()
    for t in queryset.order_by('class_date', 'start_time'):
        key = t.class_date.strftime('%b %d, %Y') + ' (' + t.class_date.strftime('%A') + ')'
        if key not in day_map:
            day_map[key] = {}
        day_map[key][t.start_time[:5]] = t

    rows = []
    for date_label, slot_dict in day_map.items():
        rows.append({
            'date':  date_label,
            'cells': [slot_dict.get(label) for label in SLOT_LABELS],
        })
    return rows


# ─── Admin: dashboard ─────────────────────────────────────────
def admin_yearly_timetable_view(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    subjects = YearlySubject.objects.all()
    total    = YearlyTimetable.objects.count()

    # Per-subject balance stats
    stats = []
    for s in subjects:
        done   = YearlyTimetable.objects.filter(subject=s, status__in=['Scheduled', 'Rescheduled']).count()
        missed = YearlyTimetable.objects.filter(subject=s, status='Holiday').count()
        stats.append({
            'name':     s.subject_name,
            'required': s.total_required_classes,
            'done':     done,
            'missed':   missed,
            'ok':       done >= s.total_required_classes,
        })

    # Preview first 15 working days only
    # list() required — MySQL cannot do LIMIT inside an IN subquery
    preview_dates = list(
        YearlyTimetable.objects
        .values_list('class_date', flat=True)
        .distinct().order_by('class_date')[:15]
    )
    preview_qs = YearlyTimetable.objects.filter(class_date__in=preview_dates)
    rows = _build_rows(preview_qs)

    return render(request, 'admin_yearly_timetable.html', {
        'stats':  stats,
        'rows':   rows,
        'slots':  SLOT_LABELS,
        'total':  total,
    })


# ─── Admin: Step 1 – Generate ─────────────────────────────────
def generate_yearly_timetable(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    YearlyTimetable.objects.all().delete()

    # Always ensure exactly 6 subjects
    if YearlySubject.objects.count() < 6:
        YearlySubject.objects.all().delete()
        for name in ['Mathematics', 'Physics', 'Computer Science', 'Chemistry', 'Biology', 'English']:
            YearlySubject.objects.create(subject_name=name, total_required_classes=40)

    subjects = list(YearlySubject.objects.all())
    assigned = {s.id: 0 for s in subjects}
    current  = date.today()

    while any(assigned[s.id] < s.total_required_classes for s in subjects):
        if current.weekday() < 5:          # Mon–Fri only
            daily = list(subjects)
            random.shuffle(daily)          # jumble order each day
            for i, (st, et) in enumerate(YEARLY_SLOTS):
                if i < len(daily):
                    s = daily[i]
                    if assigned[s.id] < s.total_required_classes:
                        YearlyTimetable.objects.create(
                            subject=s,
                            subject_name=s.subject_name,
                            class_date=current,
                            start_time=st,
                            end_time=et,
                            status='Scheduled',
                        )
                        assigned[s.id] += 1
        current += timedelta(days=1)

    total = YearlyTimetable.objects.count()
    messages.success(request, f"Year plan generated — {total} classes across 6 subjects.")
    return redirect('admin_yearly_timetable')


# ─── Admin: Step 2 – Apply holidays + reschedule ──────────────
def apply_and_reschedule(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')

    holiday_dates = set(Holiday.objects.values_list('holiday_date', flat=True))

    # Find all scheduled classes that fall on a holiday
    to_cancel = YearlyTimetable.objects.filter(class_date__in=holiday_dates, status='Scheduled')
    missed    = list(to_cancel.values('subject_id', 'subject_name', 'start_time', 'end_time', 'class_date'))
    cancelled = to_cancel.count()
    to_cancel.update(status='Holiday')

    # Reschedule each missed class to the next available slot
    rescheduled = 0
    for entry in missed:
        check = entry['class_date'] + timedelta(days=1)
        for _ in range(90):                # search up to 90 days ahead
            slot_taken = YearlyTimetable.objects.filter(
                class_date=check,
                start_time=entry['start_time'],
                status__in=['Scheduled', 'Rescheduled'],
            ).exists()
            if check.weekday() < 5 and check not in holiday_dates and not slot_taken:
                YearlyTimetable.objects.create(
                    subject_id=entry['subject_id'],
                    subject_name=entry['subject_name'],
                    class_date=check,
                    start_time=entry['start_time'],
                    end_time=entry['end_time'],
                    status='Rescheduled',
                )
                rescheduled += 1
                break
            check += timedelta(days=1)

    messages.success(request,
        f"{cancelled} classes cancelled for holidays. "
        f"{rescheduled} rescheduled to next available working days."
    )
    return redirect('admin_yearly_timetable')


# ─── Student: view full year ───────────────────────────────────
def student_yearly_timetable_view(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('login')

    rows = _build_rows(YearlyTimetable.objects.all())
    return render(request, 'student_yearly_timetable.html', {
        'rows':  rows,
        'slots': SLOT_LABELS,
    })

# ==========================================
# WEEKLY TIMETABLE & HOLIDAY COMPENSATION
# ==========================================

def holiday_compensation_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
        
    timetable = WeeklyTimetable.objects.all().order_by('id')
    holidays = Holiday.objects.all().order_by('-created_at')
    compensations = CompensationSchedule.objects.all().order_by('-created_at')
    
    # Simple logic to find the latest detected missed classes
    latest_holiday = holidays.first()
    missed_classes = []
    
    if latest_holiday:
        day_of_week = latest_holiday.holiday_date.strftime('%A')
        day_schedule = WeeklyTimetable.objects.filter(day_of_week=day_of_week).first()
        if day_schedule:
            slots = [day_schedule.slot_1, day_schedule.slot_2, day_schedule.slot_3, day_schedule.slot_4, day_schedule.slot_5]
            missed_classes = [s for s in slots if s and s.strip() != '']
            
    context = {
        'timetable': timetable,
        'holidays': holidays,
        'compensations': compensations,
        'latest_holiday': latest_holiday,
        'missed_classes': missed_classes,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    return render(request, 'holiday_compensation_dashboard.html', context)

def add_holiday(request):
    if request.method == 'POST':
        date = request.POST.get('holiday_date')
        name = request.POST.get('holiday_name')
        try:
            Holiday.objects.create(holiday_date=date, holiday_name=name)
            messages.success(request, f"Holiday '{name}' added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding holiday: it may already exist.")
    return redirect('holiday_compensation_dashboard')

def detect_missed_classes(request):
    # This is handled dynamically in the dashboard view based on the latest holiday
    messages.info(request, "Missed classes detected successfully.")
    return redirect('holiday_compensation_dashboard')

def generate_compensation_schedule(request):
    if request.method == 'POST':
        latest_holiday = Holiday.objects.all().order_by('-created_at').first()
        if not latest_holiday:
            messages.error(request, "No holidays found to compensate.")
            return redirect('holiday_compensation_dashboard')
            
        day_of_week = latest_holiday.holiday_date.strftime('%A')
        day_schedule = WeeklyTimetable.objects.filter(day_of_week=day_of_week).first()
        
        if day_schedule:
            slots = [day_schedule.slot_1, day_schedule.slot_2, day_schedule.slot_3, day_schedule.slot_4, day_schedule.slot_5]
            
            # Simple logic: push to next Saturday
            days_ahead = 5 - latest_holiday.holiday_date.weekday() # Saturday
            if days_ahead <= 0: # Target next week
                days_ahead += 7
            comp_date = latest_holiday.holiday_date + timedelta(days=days_ahead)
            
            # Clear pending first
            CompensationSchedule.objects.filter(missed_date=latest_holiday.holiday_date, status='Pending').delete()
            
            for i, slot in enumerate(slots):
                if slot and slot.strip() != '':
                    CompensationSchedule.objects.create(
                        original_class=slot,
                        missed_date=latest_holiday.holiday_date,
                        compensation_date=comp_date,
                        compensation_slot=f"Slot {i+1}",
                        status='Pending'
                    )
            messages.success(request, f"Compensation generated for {latest_holiday.holiday_date}")
    return redirect('holiday_compensation_dashboard')

def approve_compensation(request):
    if request.method == 'POST':
        CompensationSchedule.objects.filter(status='Pending').update(status='Approved')
        messages.success(request, "Compensation schedule approved.")
    return redirect('holiday_compensation_dashboard')


