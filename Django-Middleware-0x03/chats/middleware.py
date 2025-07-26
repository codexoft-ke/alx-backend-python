"""
Custom Middleware for Chat Application

This file contains various middleware components for the messaging application:
1. RequestLoggingMiddleware - Logs user requests with timestamps
2. RestrictAccessByTimeMiddleware - Restricts access during specific hours
3. OffensiveLanguageMiddleware - Rate limiting based on IP address
4. RolePermissionMiddleware - Enforces role-based permissions
"""

import logging
import time
from datetime import datetime, time as dt_time
from collections import defaultdict
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

# Configure logging for requests
import os
requests_log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'requests.log')

class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to a file with timestamp, user, and path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Write to requests.log file
        try:
            with open(requests_log_file, 'a') as f:
                f.write(log_message)
        except Exception as e:
            print(f"Logging error: {e}")
        
        # Process the request
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the messaging app during certain hours.
    Access is denied outside 6 AM to 9 PM.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.start_time = dt_time(6, 0)  # 6:00 AM
        self.end_time = dt_time(21, 0)   # 9:00 PM
    
    def __call__(self, request):
        current_time = datetime.now().time()
        
        # Check if current time is outside allowed hours
        if not (self.start_time <= current_time <= self.end_time):
            return HttpResponseForbidden(
                "Access denied: Chat service is only available between 6:00 AM and 9:00 PM"
            )
        
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Middleware that implements rate limiting based on IP address.
    Limits users to 5 messages per minute.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = defaultdict(list)  # IP -> list of timestamps
        self.max_requests = 5  # Maximum requests per minute
        self.time_window = 60  # 60 seconds (1 minute)
    
    def __call__(self, request):
        # Only apply rate limiting to POST requests (sending messages)
        if request.method == 'POST':
            client_ip = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old timestamps outside the time window
            self.request_counts[client_ip] = [
                timestamp for timestamp in self.request_counts[client_ip]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if user has exceeded the limit
            if len(self.request_counts[client_ip]) >= self.max_requests:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.max_requests} messages per minute'
                    },
                    status=429
                )
            
            # Add current timestamp
            self.request_counts[client_ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware:
    """
    Middleware that enforces role-based permissions.
    Only admin and moderator users can access specific actions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_paths = [
            '/api/conversations/',
            '/api/messages/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Check if the path requires role-based access
        requires_role_check = any(
            request.path.startswith(path) for path in self.protected_paths
        )
        
        if requires_role_check:
            # Check if user is authenticated
            if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            # Check if user has admin or moderator role
            user = request.user
            is_admin = user.is_staff or user.is_superuser
            is_moderator = hasattr(user, 'role') and user.role == 'moderator'
            
            if not (is_admin or is_moderator):
                return HttpResponseForbidden(
                    "Access denied: Admin or moderator role required"
                )
        
        response = self.get_response(request)
        return response
