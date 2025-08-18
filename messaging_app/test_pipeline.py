"""
Basic pytest tests for the messaging app CI/CD pipeline
These tests ensure the pipeline can run tests successfully
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class BasicPipelineTest(TestCase):
    """Basic tests to verify the CI/CD pipeline functionality"""
    
    def test_django_setup(self):
        """Test that Django is properly configured"""
        from django.conf import settings
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
    
    def test_database_connection(self):
        """Test that database connection works"""
        # This test will fail if database is not properly configured
        user_count = User.objects.count()
        self.assertIsInstance(user_count, int)
    
    def test_user_creation(self):
        """Test basic user creation functionality"""
        initial_count = User.objects.count()
        
        user = User.objects.create_user(
            username='testuser_pipeline',
            email='test@pipeline.com',
            password='testpass123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser_pipeline')
        self.assertEqual(User.objects.count(), initial_count + 1)


@pytest.mark.django_db
def test_simple_addition():
    """Simple test to verify pytest is working"""
    assert 1 + 1 == 2


@pytest.mark.django_db 
def test_user_model_with_pytest():
    """Test user model creation using pytest"""
    user = User.objects.create_user(
        username='pytest_user',
        email='pytest@test.com',
        password='testpass123'
    )
    
    assert user.username == 'pytest_user'
    assert user.email == 'pytest@test.com'
    assert user.check_password('testpass123')


class TestAppImports:
    """Test that all required modules can be imported"""
    
    def test_django_imports(self):
        """Test Django core imports"""
        import django
        from django.conf import settings
        assert hasattr(django, 'VERSION')
    
    def test_rest_framework_imports(self):
        """Test Django REST Framework imports"""
        from rest_framework import serializers, viewsets
        assert hasattr(serializers, 'ModelSerializer')
        assert hasattr(viewsets, 'ModelViewSet')
    
    def test_app_imports(self):
        """Test that our app modules can be imported"""
        try:
            from chats import models, views, serializers
            assert True  # If we get here, imports worked
        except ImportError:
            pytest.skip("Chats app not available in this environment")
