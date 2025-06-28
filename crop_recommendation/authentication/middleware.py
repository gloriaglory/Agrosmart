from django.utils.deprecation import MiddlewareMixin

class CSRFExemptAPIMiddleware(MiddlewareMixin):
    """
    Middleware to exempt API endpoints from CSRF protection.
    """
    def process_request(self, request):
        # Exempt API endpoints from CSRF protection
        if request.path.startswith('/api/') or request.path.startswith('/detector/'):
            setattr(request, '_dont_enforce_csrf_checks', True)