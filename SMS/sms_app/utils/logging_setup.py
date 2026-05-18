"""
logging_setup.py
----------------
Attaches the TruncateAjaxFilter to Django's django.server logger so that
massive DataTables AJAX query strings no longer flood the terminal.

Called once from SmsAppConfig.ready() in apps.py.
No settings.py changes are required.
"""

import logging
from sms_app.utils.log_filters import TruncateAjaxFilter


def configure_logging():
    """
    Attach TruncateAjaxFilter to the django.server logger.

    django.server is the logger Django's runserver uses to print every
    HTTP request line. DataTables server-side AJAX endpoints send a
    3-5 KB URL on every page-change / search keystroke, e.g.:

      "GET /SMS/invoice_pending_report_ajax/?draw=1&columns%5B0%5D...
       (3 KB of URL-encoded column definitions) HTTP/1.1" 200 4321

    The filter replaces that with a short summary:

      "GET /SMS/invoice_pending_report_ajax/?[48 DataTables params — truncated]
       HTTP/1.1" 200 4321
    """
    server_logger = logging.getLogger('django.server')

    # Guard against double-attachment on autoreload
    if not any(isinstance(f, TruncateAjaxFilter) for f in server_logger.filters):
        server_logger.addFilter(TruncateAjaxFilter())
