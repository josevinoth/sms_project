from django.contrib import messages

class ClearMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Handle deleted/missing record exceptions globally
        if isinstance(exception, ObjectDoesNotExist):
            return HttpResponse(
                "<script>"
                "alert('The record you are trying to access does not exist or has been deleted.');"
                "if (document.referrer && document.referrer !== window.location.href) { window.location.href = document.referrer; }"
                "else { window.location.href = '/SMS/enquirynote_list/'; }"
                "</script>"
            )

        # Handle invalid ID formats (e.g., passing empty string to integer field)
        if isinstance(exception, ValueError) and ("invalid literal for int" in str(exception) or "expected a number but got" in str(exception)):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({'error': 'Invalid parameter provided.'}, status=400)
            return HttpResponse(
                "<script>"
                "alert('Invalid parameter provided. Please try again.');"
                "if (document.referrer && document.referrer !== window.location.href) { window.location.href = document.referrer; }"
                "else { window.location.href = '/'; }"
                "</script>"
            )

        # Log the unhandled exception for developers
        logger.exception(f"Unhandled server exception: {exception}")

        # Provide a friendly message for generic 500 errors
        user_message = (
            "An unexpected error occurred while processing your request. "
            "Our development team has been notified. "
            "Please try again later."
        )

        # Handle AJAX requests gracefully
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
            return JsonResponse({'error': user_message}, status=500)

        # Handle standard HTTP requests with the custom 500 template
        return render(request, '500_custom.html', {'error_message': user_message}, status=500)
