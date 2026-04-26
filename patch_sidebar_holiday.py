import os

FILES_TO_UPDATE = [
    'admin_dashboard.html',
    'admin_profile.html',
    'admin_settings.html',
    'admin_leave_dashboard.html',
    'admin_queue_dashboard.html',
    'admin_lost_found_dashboard.html'
]

def add_holiday_comp_link(filename):
    path = os.path.join(r'c:\Campus Sphere\campus_project\backend_login_system\templates', filename)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    target = '<div class="menu-category">Settings</div>'
    replacement = '<a href="{% url \'holiday_compensation_dashboard\' %}" class="menu-item"><i class="bi bi-calendar-event"></i> Holiday Compensation</a>\n        \n        <div class="menu-category">Settings</div>'
    
    if target in html and 'Holiday Compensation' not in html:
        html = html.replace(target, replacement)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Updated {filename}")

for f in FILES_TO_UPDATE:
    add_holiday_comp_link(f)
