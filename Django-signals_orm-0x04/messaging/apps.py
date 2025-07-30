"""
App configuration for the messaging app.

This module contains the app configuration class that ensures
Django signals are properly imported and registered.
"""
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """
    Configuration class for the messaging app.
    
    This class ensures that Django signals are imported when the app is ready,
    which is necessary for the signal handlers to be registered and work properly.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    verbose_name = 'Messaging System'

    def ready(self):
        """
        This method is called when Django starts.
        
        It imports the signals module to ensure that all signal handlers
        are registered and will be triggered when the corresponding events occur.
        """
        try:
            # Import signals to register them
            import messaging.signals
            print("✅ Messaging app signals loaded successfully")
        except ImportError as e:
            print(f"❌ Error loading messaging signals: {e}")
        except Exception as e:
            print(f"❌ Unexpected error in messaging app ready(): {e}")
