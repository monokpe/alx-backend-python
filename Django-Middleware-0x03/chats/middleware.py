import time
import logging
from datetime import datetime, time
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse

request_logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware:
    """
    Middleware to log request details including user, request path, and timestamp.
    """

    def __init__(self, get_response):
        """
        One-time configuration and initialization.
        The `get_response` argument is a callable provided by Django.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for each request.
        """
        request_logger.info(
            f"Request: {request.method} {request.path} at {datetime.now().isoformat()}"
        )

        user = "Anonymous"
        if request.user.is_authenticated:
            user = f"User_ID:{request.user.pk}"

        log_message = f"User: {user} - Path: {request.path} - Method: {request.method}"
        request_logger.info(log_message)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for each request.
        It checks the current time and denies access if outside allowed hours.
        """
        start_time = time(6, 0)
        end_time = time(21, 0)  # 9:00 PM (21:00 in 24-hour format)

        current_time = datetime.now().time()

        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden(
                "Access to the service is restricted at this time."
            )

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
        self.limit = 5
        self.time_window = 60  # seconds

    def __call__(self, request):
        """
        This method is called for each request.
        It checks and enforces a rate limit on POST requests to message endpoints.
        """
        if request.method == "POST" and "messages" in request.path:
            ip_address = request.META.get("REMOTE_ADDR")
            if not ip_address:
                return HttpResponseForbidden("Could not determine IP address.")

            current_time = time.time()
            request_timestamps = self.requests.get(ip_address, [])
            recent_timestamps = [
                ts for ts in request_timestamps if current_time - ts < self.time_window
            ]

            if len(recent_timestamps) >= self.limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=429,
                )

            recent_timestamps.append(current_time)
            self.requests[ip_address] = recent_timestamps

        response = self.get_response(request)
        return response


class RolepermissionMiddleware:
    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for each request.
        It checks if the user has the 'ADMIN' role for paths under /admin/.
        """
        if request.path.startswith("/admin/"):
            if not request.user.is_authenticated:
                # Let Django's default admin handling take care of redirecting to the login page.
                pass

            elif hasattr(request.user, "role") and request.user.role != "ADMIN":
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )

        response = self.get_response(request)
        return response
