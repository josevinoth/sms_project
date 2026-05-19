import logging
import re


# Patterns in the request path that are known to produce massive query strings
# (DataTables server-side AJAX endpoints).
_AJAX_URL_PATTERNS = re.compile(
    r'(_ajax/|_ajax$|halting_report_ajax|movementwise_pl_report_ajax'
    r'|customerwise_pl_report_ajax|pod_pending_report_ajax'
    r'|enquiry_pending_report_ajax|invoice_pending_report_ajax'
    r'|consignmentdetail_list_ajax|tripdetail_list_ajax|tripclosure_list_ajax)',
    re.IGNORECASE,
)

# Max length to allow before we truncate the logged URL portion
_MAX_URL_DISPLAY = 120


class TruncateAjaxFilter(logging.Filter):
    """
    Attached to the ``django.server`` logger.

    For DataTables AJAX requests the full URL can be several kilobytes long
    (column definitions, search params, order params …).  Printing that to the
    terminal on every keystroke in a search box:
      • floods the console making it unreadable
      • wastes I/O on every request
      • can noticeably slow the development server

    This filter keeps the log line but replaces the bloated query string with a
    short summary so the terminal stays useful.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        # record.args for django.server is a tuple:
        #   (method_and_path, status_code, response_size)
        # e.g. ("GET /SMS/invoice_pending_report_ajax/?draw=1&columns%5B0%5D... HTTP/1.1", 200, 1234)
        if record.args and isinstance(record.args, tuple) and len(record.args) >= 1:
            path_str = str(record.args[0])

            if _AJAX_URL_PATTERNS.search(path_str):
                # Extract just the path before the '?'
                if '?' in path_str:
                    base, qs = path_str.split('?', 1)
                    # Count how many DataTables params are in there
                    param_count = qs.count('&') + 1
                    short = f"{base}?[{param_count} DataTables params — truncated]"
                    record.args = (short,) + record.args[1:]
                # If no '?' but still matches, leave it (unusual)
                return True

            # Truncate any other very long request lines (e.g. POST bodies in logs)
            if len(path_str) > _MAX_URL_DISPLAY:
                short = path_str[:_MAX_URL_DISPLAY] + '… [truncated]'
                record.args = (short,) + record.args[1:]

        # Also truncate the message string itself if somehow it's huge
        if isinstance(record.msg, str) and len(record.msg) > 300:
            record.msg = record.msg[:300] + '… [truncated]'

        return True


class SuppressStaticFilter(logging.Filter):
    """
    Optionally suppress noisy static-file requests from the terminal log.
    Add this filter to 'django.server' handler if static file requests
    are cluttering the console (they always return 200/304 and are not useful).
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        if record.args and isinstance(record.args, tuple) and len(record.args) >= 1:
            path = str(record.args[0])
            if '/static/' in path or '/favicon.ico' in path:
                return False  # suppress
        return True
