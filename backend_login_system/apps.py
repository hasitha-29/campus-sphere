from django.apps import AppConfig


class BackendLoginSystemConfig(AppConfig):
    name = 'backend_login_system'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_demo_accounts, sender=self)


def create_demo_accounts(sender, **kwargs):
    """
    Automatically creates demo Admin and Student accounts
    after every database migration (i.e., after every Render deploy).
    This ensures accounts always exist even when the SQLite DB resets.
    """
    try:
        from backend_login_system.models import CustomUser
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_user(username='admin', password='admin123', role='admin')
            print('[CampusSphere] Demo admin account created.')
        if not CustomUser.objects.filter(username='student').exists():
            CustomUser.objects.create_user(username='student', password='student123', role='student')
            print('[CampusSphere] Demo student account created.')
    except Exception as e:
        print(f'[CampusSphere] Could not create demo accounts: {e}')
