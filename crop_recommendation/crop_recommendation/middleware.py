import time
import json
import logging
import threading
import functools
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

# Use the ngrok_style logger as configured in settings.py
logger = logging.getLogger('ngrok_style')

# Default request timeout in seconds
DEFAULT_REQUEST_TIMEOUT = 30

class CSRFExemptAPIMiddleware(MiddlewareMixin):
    """
    Middleware to exempt API endpoints from CSRF protection.
    """
    def process_request(self, request):
        # Exempt API endpoints from CSRF protection
        if request.path.startswith('/api/') or request.path.startswith('/detector/'):
            setattr(request, '_dont_enforce_csrf_checks', True)


class TimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle request timeouts to prevent hanging requests.
    Terminates requests that exceed the timeout by raising an exception.
    """
    def process_request(self, request):
        # Set a timeout for the request
        request.timeout_timer = None
        request.timeout_exceeded = False
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Store the original view function
        request.original_view_func = view_func

        # Create a timeout function
        def timeout_function():
            logger.warning(f"Request timeout: {request.method} {request.path} exceeded {DEFAULT_REQUEST_TIMEOUT} seconds")
            # Mark the request as timed out
            request.timeout_exceeded = True

        # Start a timer to check for timeout
        request.timeout_timer = threading.Timer(DEFAULT_REQUEST_TIMEOUT, timeout_function)
        request.timeout_timer.daemon = True  # Allow the timer to be terminated when the main thread exits
        request.timeout_timer.start()

        # Check if the request has already timed out
        if getattr(request, 'timeout_exceeded', False):
            # If timeout was exceeded, return a timeout response
            logger.error(f"Terminating hanging request: {request.method} {request.path}")
            return HttpResponse(
                json.dumps({"error": "Request timed out"}),
                status=408,
                content_type="application/json"
            )

        # Continue with the original view function
        return None

    def process_response(self, request, response):
        # Cancel the timeout timer if it exists
        if hasattr(request, 'timeout_timer') and request.timeout_timer:
            request.timeout_timer.cancel()
        return response

    def process_exception(self, request, exception):
        # Cancel the timeout timer if it exists
        if hasattr(request, 'timeout_timer') and request.timeout_timer:
            request.timeout_timer.cancel()
        return None


class NgrokStyleLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all HTTP requests and responses in a format similar to ngrok.
    Also captures request body for non-GET requests early to avoid RawPostDataException.
    """
    def process_request(self, request):
        # Store the start time
        request.start_time = time.time()

        # For non-GET requests, store the body content early before it's consumed
        if request.method != 'GET' and hasattr(request, 'body'):
            try:
                # Save the raw body content as a string
                request._body_copy = request.body.decode('utf-8')
            except Exception:
                # In case we can't decode as UTF-8
                request._body_copy = None

        return None

    def process_response(self, request, response):
        # Calculate response time
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = int(duration * 1000)  # Convert to milliseconds
        else:
            duration_ms = 0

        # Get response size
        content_length = len(response.content) if hasattr(response, 'content') else 0

        # Get request headers
        request_headers = {}
        for header, value in request.META.items():
            if header.startswith('HTTP_'):
                # Convert HTTP_ACCEPT to Accept
                header_name = header[5:].replace('_', '-').title()
                request_headers[header_name] = value

        # Get response headers
        response_headers = {}
        for header, value in response.items():
            response_headers[header] = value

        # Format the log message similar to ngrok
        log_message = (
            f"{request.method} {request.get_full_path()} - "
            f"Status: {response.status_code} - "
            f"Time: {duration_ms}ms - "
            f"Size: {content_length} bytes"
        )

        # Log the basic message
        logger.info(log_message)

        # Log detailed information
        detailed_log = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'method': request.method,
            'path': request.get_full_path(),
            'status_code': response.status_code,
            'duration_ms': duration_ms,
            'size_bytes': content_length,
            'request_headers': request_headers,
            'response_headers': response_headers,
        }

        # Log request body for non-GET requests using our saved copy
        if request.method != 'GET' and hasattr(request, '_body_copy') and request._body_copy:
            try:
                # Try to parse as JSON
                body = request._body_copy
                if body:
                    try:
                        detailed_log['request_body'] = json.loads(body)
                    except json.JSONDecodeError:
                        detailed_log['request_body'] = body
            except Exception as e:
                detailed_log['request_body_error'] = str(e)

        # Try to log response body for JSON responses
        if 'application/json' in response.get('Content-Type', ''):
            try:
                detailed_log['response_body'] = json.loads(response.content.decode('utf-8'))
            except Exception as e:
                detailed_log['response_body_error'] = str(e)

        # Log the detailed information
        logger.debug(json.dumps(detailed_log, indent=2))

        # Also print to console for immediate visibility
        print(f"[NGROK-STYLE] {log_message}")

        return response
