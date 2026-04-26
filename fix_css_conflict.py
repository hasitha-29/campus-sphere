import os, re

TEMPLATES_DIR = r'c:\Campus Sphere\campus_project\backend_login_system\templates'

# Files that have the bad :root { --primary ... } override
TARGETS = [
    'admin_leave_dashboard.html',
    'admin_queue_dashboard.html',
    'admin_lost_found_dashboard.html',
]

BAD_ROOT_PATTERN = re.compile(r':root\s*\{[^}]+\}', re.DOTALL)

for filename in TARGETS:
    filepath = os.path.join(TEMPLATES_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the bad :root { } override that conflicts with campus.css
    new_content = BAD_ROOT_PATTERN.sub('/* CSS variables inherited from campus.css */', content, count=1)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Cleaned :root override in {filename}")
    else:
        print(f"  No :root override found in {filename}")

print("Done.")
