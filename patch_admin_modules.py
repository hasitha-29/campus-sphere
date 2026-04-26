import os

FILES_TO_UPDATE = [
    'admin_leave_dashboard.html',
    'admin_queue_dashboard.html',
    'admin_lost_found_dashboard.html'
]

SIDEBAR_HTML = """<!-- Sidebar -->
<div class="sidebar">
    <div class="sidebar-brand">
        <div class="brand-logo">CS</div>
        CampusSphere
    </div>
    
    <div class="user-profile-section">
        <div class="user-avatar">{{ user.username|make_list|first|upper }}</div>
        <div style="overflow: hidden;">
            <div class="fw-bold text-truncate" style="color: var(--primary); font-size: 0.95rem; text-transform: capitalize;">{{ user.username }}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 500;">Admin Console</div>
        </div>
    </div>
    
    <div class="sidebar-menu">
        <div class="menu-category">Overview</div>
        <a href="{% url 'admin_dashboard' %}" class="menu-item"><i class="bi bi-grid"></i> Dashboard</a>
        <a href="#" class="menu-item"><i class="bi bi-person-circle"></i> Admin Profile</a>
        
        <div class="menu-category">Applications</div>
        <a href="{% url 'admin_leave_dashboard' %}" class="menu-item __LEAVE_ACTIVE__"><i class="bi bi-airplane"></i> Leave Management</a>
        <a href="{% url 'admin_queue_dashboard' %}" class="menu-item __QUEUE_ACTIVE__"><i class="bi bi-clock-history"></i> Queue Booking</a>
        <a href="{% url 'admin_lost_found_dashboard' %}" class="menu-item __LOST_ACTIVE__"><i class="bi bi-box-seam"></i> Lost & Found</a>
        
        <div class="menu-category">Settings</div>
        <a href="#" class="menu-item"><i class="bi bi-gear"></i> System Settings</a>
    </div>
    
    <div class="p-4 border-top">
        <a href="{% url 'logout' %}" class="menu-item" style="color: var(--text-muted); padding: 0;"><i class="bi bi-box-arrow-right"></i> Sign Out</a>
    </div>
</div>

<!-- Main Content -->
<div class="main-content">
"""

def update_file(filename):
    path = os.path.join(r'c:\Campus Sphere\campus_project\backend_login_system\templates', filename)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Determine active tab
    sidebar = SIDEBAR_HTML
    sidebar = sidebar.replace('__LEAVE_ACTIVE__', 'active' if 'leave' in filename else '')
    sidebar = sidebar.replace('__QUEUE_ACTIVE__', 'active' if 'queue' in filename else '')
    sidebar = sidebar.replace('__LOST_ACTIVE__', 'active' if 'lost_found' in filename else '')

    # Find the navbar
    nav_start = html.find('<nav class="saas-navbar text-white">')
    if nav_start == -1:
        print(f"Skipping {filename}: no saas-navbar found")
        return

    nav_end = html.find('</nav>', nav_start) + 6

    # Find container
    container_start = html.find('<div class="container-fluid', nav_end)
    if container_start == -1:
        container_start = html.find('<div class="container', nav_end)
    container_end = html.find('>', container_start) + 1

    # Reconstruct body
    new_html = html[:nav_start] + sidebar + html[container_end:]
    
    # Replace closing tags
    body_end = new_html.rfind('</body>')
    # Close the .main-content div before scripts
    script_start = new_html.rfind('<script')
    if script_start != -1:
        new_html = new_html[:script_start] + '</div>\n\n' + new_html[script_start:]
    else:
        new_html = new_html[:body_end] + '</div>\n' + new_html[body_end:]
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Updated {filename}")

for f in FILES_TO_UPDATE:
    update_file(f)
