# Django imports this file automatically when it loads the sms_app package.
# We use this to attach the log filter at startup — no apps.py or settings.py
# changes are needed.
try:
    from sms_app.utils.logging_setup import configure_logging
    configure_logging()
except Exception:
    pass  # Never break startup over a logging configuration failure
