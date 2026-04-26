import os
import glob

def patch_student_links():
    templates_dir = r'c:\Campus Sphere\campus_project\backend_login_system\templates'
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this is a student template with a sidebar
            if '<div class="sidebar-menu">' in content and 'admin_dashboard' not in content:
                # Let's be safe and just replace exactly the profile link
                target1 = '<a href="#" class="menu-item"><i class="bi bi-person-circle"></i> Profile</a>'
                replacement1 = '<a href="{% url \'student_profile\' %}" class="menu-item"><i class="bi bi-person-circle"></i> Profile</a>'
                
                target2 = '<a href="#" class="menu-item "><i class="bi bi-person-circle"></i> Profile</a>'
                replacement2 = '<a href="{% url \'student_profile\' %}" class="menu-item"><i class="bi bi-person-circle"></i> Profile</a>'
                
                if target1 in content or target2 in content:
                    content = content.replace(target1, replacement1)
                    content = content.replace(target2, replacement2)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filename}")

if __name__ == '__main__':
    patch_student_links()
