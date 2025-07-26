# Custom authentication logic for chats app (if needed)
# For now, this can be used for future customizations.

from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Extend this class to customize JWT authentication behavior for the chats app.
    """
    pass
