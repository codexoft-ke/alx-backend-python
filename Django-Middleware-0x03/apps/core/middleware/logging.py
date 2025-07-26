"""
Logging Middleware

This middleware logs incoming requests and outgoing responses for debugging and auditing purposes.
It tracks request metadata including path, method, user, and response status.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming requests and outgoing responses.
    
    Logs information about:
    - Request method and path
    - User information (if authenticated)
    - Response status code
    - Request processing time
    """
    
    def process_request(self, request):
        """
        Process incoming request before it reaches the view.
        """
        request.start_time = time.time()
        
        user_info = f"User: {request.user}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        
        logger.info(
            f"Incoming Request - {request.method} {request.path} | "
            f"{user_info} | IP: {self.get_client_ip(request)}"
        )
        
        return None
    
    def process_response(self, request, response):
        """
        Process outgoing response after the view has been processed.
        """
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            user_info = f"User: {request.user}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
            
            logger.info(
                f"Outgoing Response - {request.method} {request.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"{user_info}"
            )
        
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
