import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden

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
