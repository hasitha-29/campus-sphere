from django.contrib import admin
from django.apps import apps

# Automatically register all models in this app so you can manage them in the Django Admin Panel
app = apps.get_app_config('backend_login_system')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
