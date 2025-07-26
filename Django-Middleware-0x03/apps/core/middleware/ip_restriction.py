"""
IP Restriction Middleware

This middleware blocks requests from banned IP addresses and provides
basic security filtering based on IP addresses and request headers.
"""

from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class IPRestrictionMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access based on IP addresses.
    
    Features:
    - Block requests from banned IP addresses
    - Allow requests only from whitelisted IPs (if configured)
    - Log blocked requests for security monitoring
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Get IP restrictions from settings
        self.banned_ips = getattr(settings, 'BANNED_IPS', set())
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', None)  # None means all IPs allowed
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming request to check IP restrictions.
        """
        client_ip = self.get_client_ip(request)
        
        # Check if IP is banned
        if client_ip in self.banned_ips:
            logger.warning(
                f"Blocked request from banned IP: {client_ip} | "
                f"Path: {request.path} | Method: {request.method}"
            )
            return HttpResponseForbidden(
                "Access denied: Your IP address has been blocked."
            )
        
        # Check if IP is allowed (if whitelist is configured)
        if self.allowed_ips is not None and client_ip not in self.allowed_ips:
            logger.warning(
                f"Blocked request from non-whitelisted IP: {client_ip} | "
                f"Path: {request.path} | Method: {request.method}"
            )
            return HttpResponseForbidden(
                "Access denied: Your IP address is not authorized."
            )
        
        return None
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        Handles X-Forwarded-For header for proxy situations.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
