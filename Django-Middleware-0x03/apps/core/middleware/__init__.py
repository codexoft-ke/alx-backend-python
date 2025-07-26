"""
Core Middleware Package

This package contains custom middleware components for the Django messaging application.

Available Middleware:
- RequestLoggingMiddleware: Logs incoming requests and outgoing responses
- IPRestrictionMiddleware: Blocks requests from banned IPs
- CustomAuthenticationMiddleware: Enhanced authentication checks

Usage:
Add middleware to MIDDLEWARE setting in settings.py:

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.logging.RequestLoggingMiddleware',
    'apps.core.middleware.ip_restriction.IPRestrictionMiddleware',
    'apps.core.middleware.auth.CustomAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
"""

from .logging import RequestLoggingMiddleware
from .ip_restriction import IPRestrictionMiddleware
from .auth import CustomAuthenticationMiddleware

__all__ = [
    'RequestLoggingMiddleware',
    'IPRestrictionMiddleware', 
    'CustomAuthenticationMiddleware',
]