import os

TEMPLATES_DIR = r'c:\Campus Sphere\campus_project\backend_login_system\templates'

# The correct sidebar HTML to inject
SIDEBAR_HTML = '''<!-- Sidebar -->
<div class="sidebar">
    <div class="sidebar-brand" style="padding:20px 18px !important; border-bottom:1px solid rgba(255,255,255,0.07) !important; display:flex !important; align-items:center !important; flex-direction:row !important; gap:10px !important;">
        <div class="brand-logo" style="width:32px !important;height:32px !important;background:rgba(255,255,255,0.12) !important;border-radius:8px !important;display:flex !important;align-items:center !important;justify-content:center !important;font-size:0.78rem !important;font-weight:800 !important;color:#fff !important;flex-shrink:0 !important;">CS</div>
        <span style="font-size:0.95rem !important;font-weight:700 !important;color:#fff !important;letter-spacing:-0.2px;">CampusSphere</span>
    </div>

    <div style="padding:14px 16px;margin:10px 10px 0;border-radius:10px;background:rgba(255,255,255,0.05);display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;border-radius:50%;background:#3b72b0;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;flex-shrink:0;">{{ user.username|make_list|first|upper }}</div>
        <div style="overflow:hidden;">
            <div style="font-size:0.85rem;font-weight:600;color:#fff;text-transform:capitalize;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ user.username }}</div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.45);font-weight:500;">Admin Console</div>
        </div>
    </div>

    <div class="sidebar-menu">
        <div class="menu-category">Overview</div>
        <a href="{% url 'admin_dashboard' %}" class="menu-item"><i class="bi bi-grid"></i> Dashboard</a>
        <a href="{% url 'admin_profile' %}" class="menu-item"><i class="bi bi-person-circle"></i> Admin Profile</a>

        <div class="menu-category">Applications</div>
        <a href="{% url 'admin_leave_dashboard' %}" class="menu-item LEAVE_ACTIVE"><i class="bi bi-airplane"></i> Leave Management</a>
        <a href="{% url 'admin_queue_dashboard' %}" class="menu-item QUEUE_ACTIVE"><i class="bi bi-clock-history"></i> Queue Booking</a>
        <a href="{% url 'admin_lost_found_dashboard' %}" class="menu-item LF_ACTIVE"><i class="bi bi-box-seam"></i> Lost &amp; Found</a>
        <a href="{% url 'holiday_compensation_dashboard' %}" class="menu-item HC_ACTIVE"><i class="bi bi-calendar-event"></i> Holiday Compensation</a>

        <div class="menu-category">Settings</div>
        <a href="{% url 'admin_settings' %}" class="menu-item SETTINGS_ACTIVE"><i class="bi bi-gear"></i> System Settings</a>
    </div>

    <div style="padding:14px 0;border-top:1px solid rgba(255,255,255,0.07);margin-top:auto;">
        <a href="{% url 'logout' %}" class="menu-item" style="color:rgba(255,255,255,0.45) !important;"><i class="bi bi-box-arrow-right"></i> Sign Out</a>
    </div>
</div>'''

TEMPLATES = {
    'admin_leave_dashboard.html':    ('LEAVE_ACTIVE', 'active'),
    'admin_queue_dashboard.html':    ('QUEUE_ACTIVE', 'active'),
    'admin_lost_found_dashboard.html': ('LF_ACTIVE', 'active'),
    'admin_settings.html':           ('SETTINGS_ACTIVE', 'active'),
    'admin_profile.html':            (None, None),
}

def fix_sidebar(filename, active_marker, active_class):
    filepath = os.path.join(TEMPLATES_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find start and end of sidebar div
    sidebar_start = content.find('<!-- Sidebar -->')
    if sidebar_start == -1:
        print(f"  No sidebar found in {filename}, skipping.")
        return

    # Find the closing </div> of the sidebar
    # Count nested divs from sidebar_start
    search_from = content.find('<div class="sidebar">', sidebar_start)
    if search_from == -1:
        print(f"  No <div class=\"sidebar\"> in {filename}, skipping.")
        return

    depth = 0
    i = search_from
    end = -1
    while i < len(content):
        if content[i:i+4] == '<div':
            depth += 1
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                break
        i += 1

    if end == -1:
        print(f"  Could not find end of sidebar in {filename}")
        return

    # Build the sidebar with proper active state
    sidebar = SIDEBAR_HTML
    for marker in ['LEAVE_ACTIVE', 'QUEUE_ACTIVE', 'LF_ACTIVE', 'HC_ACTIVE', 'SETTINGS_ACTIVE']:
        if marker == active_marker:
            sidebar = sidebar.replace(marker, active_class or '')
        else:
            sidebar = sidebar.replace(marker, '')

    # Replace old sidebar
    new_content = content[:sidebar_start] + sidebar + content[end:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  Fixed: {filename}")

for filename, (marker, cls) in TEMPLATES.items():
    fix_sidebar(filename, marker, cls)

print("\nDone. All admin module sidebars updated.")
