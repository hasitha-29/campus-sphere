"""
Patches every CampusSphere template to use the unified design system:
  - primary:    #0f172a  (login page navy)
  - accent:     #2563eb  (login page blue)
  - background: #f8fafc
  - Admin sidebars → navy (#0f172a)
  - Student topbars → navy gradient (matching login)
  - Adds campus.css link to all templates
"""

import os
import re

TEMPLATES_DIR = r'c:\Campus Sphere\campus_project\backend_login_system\templates'

CSS_VARS = """:root {
            --primary: #0f172a;
            --primary-mid: #1e293b;
            --primary-light: #1e3a8a;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --accent-soft: #eff6ff;
            --surface: #ffffff;
            --background: #f8fafc;
            --border-color: #e2e8f0;
            --border-soft: #f1f5f9;
            --text-main: #0f172a;
            --text-mid: #475569;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            --success: #10b981; --success-bg: #d1fae5;
            --warning: #f59e0b; --warning-bg: #fef3c7;
            --danger: #ef4444;  --danger-bg: #fee2e2;
            --shadow-sm: 0 1px 3px rgba(15,23,42,0.06);
            --shadow-md: 0 4px 16px rgba(15,23,42,0.08);
        }"""

SIDEBAR_PATCH = """
        /* ── Unified Navy Sidebar ── */
        .sidebar {
            width: 240px;
            height: 100vh;
            background: #0f172a !important;
            position: fixed;
            left: 0; top: 0;
            display: flex;
            flex-direction: column;
            z-index: 1000;
            border-right: none;
        }
        .sidebar-brand { color: white !important; }
        .sidebar-brand .brand-logo { background: linear-gradient(135deg, #2563eb, #1e3a8a) !important; }
        .menu-category { color: rgba(255,255,255,0.3) !important; }
        .menu-item {
            color: rgba(255,255,255,0.6) !important;
            border-radius: 8px;
            margin-bottom: 2px;
        }
        .menu-item:hover, .menu-item.active {
            background: rgba(37,99,235,0.18) !important;
            color: white !important;
            border-left: 2px solid #2563eb !important;
        }
        .user-profile-section { background: rgba(255,255,255,0.07) !important; border-radius: 10px; }
        .user-avatar { background: #2563eb !important; }
        .user-name, .user-role { color: rgba(255,255,255,0.85) !important; }
        .user-role { color: rgba(255,255,255,0.4) !important; }
        .sidebar-footer { border-top: 1px solid rgba(255,255,255,0.08) !important; }
        .sidebar-footer a { color: rgba(255,255,255,0.5) !important; }
        .sidebar-footer a:hover { color: #ef4444 !important; }"""

TOPBAR_PATCH = """
        /* ── Unified Navy Topbar (Student) ── */
        .topbar, .navbar, header.topbar {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%) !important;
            border-bottom: none !important;
        }
        .topbar .navbar-brand, .topbar h4, .topbar .brand-name { color: white !important; }
        .topbar .btn-outline-secondary, .topbar .btn { border-color: rgba(255,255,255,0.2) !important; color: rgba(255,255,255,0.85) !important; }
        .topbar .btn:hover { background: rgba(255,255,255,0.15) !important; color: white !important; }"""

CARD_PATCH = """
        /* ── Unified Card + Button styles ── */
        .btn-primary, .btn-accent {
            background: #2563eb !important;
            border-color: #2563eb !important;
            color: white !important;
        }
        .btn-primary:hover { background: #1d4ed8 !important; border-color: #1d4ed8 !important; transform: translateY(-1px); }
        .form-control:focus, .form-select:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
        }"""

STATIC_TAG = "{% load static %}\n    "
CSS_LINK   = '<link rel="stylesheet" href="{% static \'css/campus.css\' %}">'

patched = []
skipped = []

for fname in os.listdir(TEMPLATES_DIR):
    if not fname.endswith('.html'):
        continue
    if fname == 'login.html':   # keep login as-is
        skipped.append(fname)
        continue

    fpath = os.path.join(TEMPLATES_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = False

    # 1. Add {% load static %} if not present
    if '{% load static %}' not in html:
        html = html.replace('<head>', '<head>\n    ' + '{% load static %}', 1)
        changed = True

    # 2. Add campus.css link after Bootstrap link
    if 'campus.css' not in html:
        html = html.replace(
            '</style>',
            '</style>\n    ' + CSS_LINK,
            1
        )
        changed = True

    # 3. Inject unified CSS vars (replace existing :root block if present)
    if ':root {' in html:
        html = re.sub(r':root\s*\{[^}]*\}', CSS_VARS, html, count=1, flags=re.DOTALL)
        changed = True

    # 4. Inject sidebar patch before </style>
    if 'sidebar' in html and '/* ── Unified Navy Sidebar' not in html:
        html = html.replace('</style>', SIDEBAR_PATCH + '\n        </style>', 1)
        changed = True

    # 5. Inject topbar patch (student pages)
    if ('topbar' in html or 'navbar' in html.lower()) and '/* ── Unified Navy Topbar' not in html:
        if '</style>' in html:
            html = html.replace('</style>', TOPBAR_PATCH + '\n        </style>', 1)
            changed = True

    # 6. Card/button patch
    if '/* ── Unified Card' not in html and '</style>' in html:
        html = html.replace('</style>', CARD_PATCH + '\n        </style>', 1)
        changed = True

    # 7. Fix body background
    html = html.replace("background-color: #f0f2f5", "background-color: #f8fafc")
    html = html.replace("background-color: #eef2f7", "background-color: #f8fafc")
    html = html.replace("background: #f0f2f5",       "background: #f8fafc")

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)

    patched.append(fname)

print(f"\nDONE: Patched {len(patched)} templates:")
for p in sorted(patched):
    print(f"   {p}")
print(f"\nSKIPPED: {skipped}")
