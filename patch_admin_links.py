import os

FILES_TO_UPDATE = [
    'admin_dashboard.html',
    'admin_leave_dashboard.html',
    'admin_queue_dashboard.html',
    'admin_lost_found_dashboard.html'
]

def update_links(filename):
    path = os.path.join(r'c:\Campus Sphere\campus_project\backend_login_system\templates', filename)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace profile link
    html = html.replace('<a href="#" class="menu-item"><i class="bi bi-person-circle"></i> Admin Profile</a>',
                        '<a href="{% url \'admin_profile\' %}" class="menu-item"><i class="bi bi-person-circle"></i> Admin Profile</a>')
    
    # Replace settings link
    html = html.replace('<a href="#" class="menu-item"><i class="bi bi-gear"></i> System Settings</a>',
                        '<a href="{% url \'admin_settings\' %}" class="menu-item"><i class="bi bi-gear"></i> System Settings</a>')
                        
    # Update active class if needed for profile
    if 'profile' in filename:
        html = html.replace('<a href="{% url \'admin_profile\' %}" class="menu-item">', '<a href="{% url \'admin_profile\' %}" class="menu-item active">')
        html = html.replace('<a href="{% url \'admin_dashboard\' %}" class="menu-item active">', '<a href="{% url \'admin_dashboard\' %}" class="menu-item">')
    
    if 'settings' in filename:
        html = html.replace('<a href="{% url \'admin_settings\' %}" class="menu-item">', '<a href="{% url \'admin_settings\' %}" class="menu-item active">')
        html = html.replace('<a href="{% url \'admin_dashboard\' %}" class="menu-item active">', '<a href="{% url \'admin_dashboard\' %}" class="menu-item">')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {filename}")

for f in FILES_TO_UPDATE:
    update_links(f)
