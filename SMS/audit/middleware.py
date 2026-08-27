import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            # Fallback to session user_id if logged in via custom session
            ses_user_id = request.session.get('ses_userID') if hasattr(request, 'session') else None
            if ses_user_id:
                from django.contrib.auth.models import User
                user = User.objects.filter(pk=ses_user_id).first()
            else:
                user = None

        _thread_locals.user = user if getattr(user, 'is_authenticated', False) else None
        response = self.get_response(request)
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response


