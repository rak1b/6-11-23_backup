from django.apps import AppConfig


class UtilityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utility'

    def ready(self):
        import utility.signals