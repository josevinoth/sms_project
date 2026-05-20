from django.apps import AppConfig


class SmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms_app'

    def ready(self):
        from sms_app.utils.logging_setup import configure_logging
        configure_logging()
