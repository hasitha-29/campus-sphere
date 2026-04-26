from django.urls import path
from . import views

urlpatterns = [
    path('', views.about_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-profile/', views.admin_profile_view, name='admin_profile'),
    path('admin-settings/', views.admin_settings_view, name='admin_settings'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-profile/', views.student_profile_view, name='student_profile'),
    
    # Leave Management routes
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('my-leaves/', views.my_leaves, name='my_leaves'),
    path('admin-leave-dashboard/', views.admin_leave_dashboard, name='admin_leave_dashboard'),
    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    
    # Queue Booking routes
    path('book-slot/', views.book_slot_view, name='book_slot'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('admin-queue-dashboard/', views.admin_queue_dashboard, name='admin_queue_dashboard'),
    path('start-queue/<int:booking_id>/', views.start_queue, name='start_queue'),
    path('verify-otp/<int:booking_id>/', views.verify_otp, name='verify_otp'),
    
    # Lost & Found routes
    path('report-lost/', views.report_lost_view, name='report_lost'),
    path('report-found/', views.report_found_view, name='report_found'),
    path('my-reports/', views.my_reports_view, name='my_reports'),
    path('admin-lost-found/', views.admin_lost_found_dashboard, name='admin_lost_found_dashboard'),
    path('mark-matched/<str:item_type>/<int:item_id>/', views.mark_as_matched, name='mark_as_matched'),
    path('close-report/<str:item_type>/<int:item_id>/', views.close_report, name='close_report'),

    # Reschedule routes
    path('reschedule-request/', views.reschedule_request_view, name='reschedule_request'),
    path('my-reschedules/', views.my_reschedules_view, name='my_reschedules'),
    path('admin-reschedule-dashboard/', views.admin_reschedule_dashboard_view, name='admin_reschedule_dashboard'),
    path('approve-reschedule/<int:reschedule_id>/', views.approve_reschedule, name='approve_reschedule'),
    path('reject-reschedule/<int:reschedule_id>/', views.reject_reschedule, name='reject_reschedule'),

    # Smart Class Rescheduling routes
    path('student-timetable/', views.student_timetable_view, name='student_timetable'),
    path('admin-class-reschedule/', views.admin_class_reschedule_view, name='admin_class_reschedule'),
    path('detect-missed-classes/', views.detect_missed_classes, name='detect_missed_classes'),
    path('auto-reschedule/', views.auto_reschedule, name='auto_reschedule'),
    path('approve-class-reschedule/<int:rc_id>/', views.approve_class_reschedule, name='approve_class_reschedule'),

    # Holiday Compensation Module
    path('holiday-compensation/', views.holiday_compensation_dashboard, name='holiday_compensation_dashboard'),
    path('holiday-compensation/add/', views.add_holiday, name='add_holiday'),
    path('holiday-compensation/detect/', views.detect_missed_classes, name='detect_missed_classes_comp'),
    path('holiday-compensation/generate/', views.generate_compensation_schedule, name='generate_compensation_schedule'),
    path('holiday-compensation/approve/', views.approve_compensation, name='approve_compensation'),

    path('admin-timetable-dashboard/', views.admin_timetable_dashboard_view, name='admin_timetable_dashboard'),
    path('generate-timetable/', views.generate_timetable, name='generate_timetable'),
    path('student-weekly-timetable/', views.student_weekly_timetable_view, name='student_weekly_timetable'),

    # Yearly Timetable Routes
    path('admin-yearly-timetable/', views.admin_yearly_timetable_view, name='admin_yearly_timetable'),
    path('generate-yearly-timetable/', views.generate_yearly_timetable, name='generate_yearly_timetable'),
    path('apply-and-reschedule/', views.apply_and_reschedule, name='apply_and_reschedule'),
    path('student-yearly-timetable/', views.student_yearly_timetable_view, name='student_yearly_timetable'),
]
