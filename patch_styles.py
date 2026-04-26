import os

files = [
    'apply_leave.html', 'book_slot.html', 'report_lost.html', 'report_found.html',
    'my_reports.html', 'my_leaves.html', 'my_bookings.html', 'reschedule_request.html',
    'my_reschedules.html', 'holiday_compensation_dashboard.html'
]
base_dir = r'c:\Campus Sphere\campus_project\backend_login_system\templates'

for f in files:
    filepath = os.path.join(base_dir, f)
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace body style
    content = content.replace(
        'body {\n            background-color: var(--background);',
        'body {\n            background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%);\n            background-attachment: fixed;'
    )
    
    # Replace premium-card style
    content = content.replace(
        '.premium-card {\n            background: var(--surface);',
        '.premium-card {\n            background: rgba(255, 255, 255, 0.85);\n            backdrop-filter: blur(12px);'
    )
    
    # Replace saas-navbar class
    content = content.replace('<nav class="saas-navbar">', '<nav class="navbar topbar py-3 shadow-sm">')
    
    # Fix the brand name color
    content = content.replace('color: var(--primary); letter-spacing: -0.5px;', 'color: white; letter-spacing: -0.5px;')
    content = content.replace('color: var(--primary);letter-spacing: -0.5px;', 'color: white; letter-spacing: -0.5px;')
    
    # Fix the badge
    content = content.replace('background-color: #f1f5f9; color: #64748b;', 'background-color: rgba(255,255,255,0.15); color: #ffffff;')
    
    # Fix the buttons inside navbar to look good on navy
    content = content.replace('class="btn btn-sm btn-light border fw-semibold text-muted"', 'class="btn btn-sm btn-outline-light fw-semibold"')
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

print("Patching complete.")
