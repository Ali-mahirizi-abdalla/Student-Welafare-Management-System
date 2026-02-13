from django.apps import AppConfig


class HmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hms'
    verbose_name = 'Student Welfare Management'

    def ready(self):
        # Import your signals when the app is ready
        import hms.signals
