from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'  # Note: 'apps.hr' not just 'hr'
    label = 'dashboard'