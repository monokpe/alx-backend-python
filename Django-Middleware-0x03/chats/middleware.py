import logging
from datetime import datetime

request_logger = logging.getLogger('request_logger')

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
            # We use user.pk as it's a reliable identifier. Email could be long.
            user = f"User_ID:{request.user.pk}" 
        
        # Log the request details using our configured logger
        log_message = f"User: {user} - Path: {request.path} - Method: {request.method}"
        request_logger.info(log_message)

        # --- This line calls the next middleware in the chain, or the view if it's the last one. ---
        response = self.get_response(request)

        # --- Code to be executed for each request/response after the view is called. ---
        # For this task, we don't need to do anything with the response.
        
        return response