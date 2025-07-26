"""
Custom Authentication Middleware

This middleware provides additional authentication checks and user validation
beyond Django's default authentication middleware.
"""

from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomAuthenticationMiddleware(MiddlewareMixin):
    """
    Custom authentication middleware for additional user validation.
    
    Features:
    - Check if user account is active
    - Enforce authentication for protected paths
    - Log authentication attempts
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define paths that require authentication
        self.protected_paths = getattr(settings, 'PROTECTED_PATHS', [
            '/api/conversations/',
            '/api/messages/',
            '/admin/',
        ])
        
        # Define paths that should skip authentication
        self.public_paths = getattr(settings, 'PUBLIC_PATHS', [
            '/api/token/',
            '/api/token/refresh/',
            '/api/token/verify/',
            '/api-auth/',
        ])
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process request to check authentication requirements.
        """
        path = request.path
        
        # Skip authentication check for public paths
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return None
        
        # Check if path requires authentication
        requires_auth = any(path.startswith(protected_path) for protected_path in self.protected_paths)
        
        if requires_auth:
            # Check if user is authenticated
            if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
                logger.warning(
                    f"Unauthenticated access attempt to protected path: {path} | "
                    f"IP: {self.get_client_ip(request)}"
                )
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            # Check if user account is active
            if not request.user.is_active:
                logger.warning(
                    f"Inactive user access attempt: {request.user.username} | "
                    f"Path: {path}"
                )
                return JsonResponse(
                    {'error': 'Account is inactive'},
                    status=403
                )
        
        return None
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
