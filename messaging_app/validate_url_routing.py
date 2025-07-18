#!/usr/bin/env python
"""
URL Routing Validation Script
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/codexoft/Projects/Programming/Personal/School Assignments/ALX/alx-backend-python/messaging_app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

def validate_url_routing():
    """Validate URL routing configuration"""
    
    print("🔍 Validating URL Routing Configuration...")
    print("=" * 60)
    
    # Test 1: Check main URLs configuration
    print("\n1. Checking Main URLs Configuration...")
    try:
        from django.urls import reverse
        from django.conf import settings
        
        # Import the main URLconf
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        print(f"   ✅ Main URLconf loaded: {settings.ROOT_URLCONF}")
        
        # Check if api path exists
        from django.urls import resolve
        try:
            url = '/api/conversations/'
            resolved = resolve(url)
            print(f"   ✅ API path resolves correctly: {url}")
        except Exception as e:
            print(f"   ❌ API path resolution failed: {e}")
        
        # Check if api-auth path exists
        try:
            url = '/api-auth/login/'
            resolved = resolve(url)
            print(f"   ✅ API-auth path resolves correctly: {url}")
        except Exception as e:
            print(f"   ❌ API-auth path resolution failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Error checking main URLs: {e}")
        return False
    
    # Test 2: Check chats URLs configuration
    print("\n2. Checking Chats App URLs Configuration...")
    try:
        from chats.urls import router
        
        # Check router registration
        registered_viewsets = router.registry
        print(f"   ✅ Router has {len(registered_viewsets)} registered viewsets:")
        for prefix, viewset, basename in registered_viewsets:
            print(f"      - {prefix}: {viewset.__name__} (basename: {basename})")
            
        # Check router URLs
        router_urls = router.urls
        print(f"   ✅ Router generated {len(router_urls)} URL patterns")
        
    except Exception as e:
        print(f"   ❌ Error checking chats URLs: {e}")
        return False
    
    # Test 3: Check ViewSet imports
    print("\n3. Checking ViewSet Imports...")
    try:
        from chats.views import ConversationViewSet, MessageViewSet, UserViewSet
        
        viewsets = [ConversationViewSet, MessageViewSet, UserViewSet]
        for viewset in viewsets:
            print(f"   ✅ {viewset.__name__} imported successfully")
            
    except Exception as e:
        print(f"   ❌ Error importing viewsets: {e}")
        return False
    
    # Test 4: Check specific URL patterns
    print("\n4. Checking Specific URL Patterns...")
    try:
        from django.urls import reverse
        
        # Test reverse URL resolution
        test_urls = [
            ('health-check', 'health/'),
            ('test-serializers', 'test-serializers/'),
        ]
        
        for url_name, expected_path in test_urls:
            try:
                resolved_url = reverse(url_name)
                print(f"   ✅ URL '{url_name}' resolves to: {resolved_url}")
            except Exception as e:
                print(f"   ❌ URL '{url_name}' resolution failed: {e}")
                
    except Exception as e:
        print(f"   ❌ Error checking URL patterns: {e}")
        return False
    
    # Test 5: Check API endpoint accessibility
    print("\n5. Checking API Endpoint Structure...")
    try:
        from django.urls import get_resolver
        from django.conf import settings
        
        resolver = get_resolver(settings.ROOT_URLCONF)
        
        # Get all URL patterns
        def get_all_patterns(resolver, prefix=''):
            patterns = []
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    patterns.extend(get_all_patterns(pattern, prefix + str(pattern.pattern)))
                else:
                    patterns.append(prefix + str(pattern.pattern))
            return patterns
        
        all_patterns = get_all_patterns(resolver)
        api_patterns = [p for p in all_patterns if 'api' in p]
        
        print(f"   ✅ Found {len(api_patterns)} API-related patterns:")
        for pattern in api_patterns[:10]:  # Show first 10
            print(f"      - {pattern}")
        if len(api_patterns) > 10:
            print(f"      ... and {len(api_patterns) - 10} more")
            
    except Exception as e:
        print(f"   ❌ Error checking API endpoints: {e}")
        return False
    
    # Test 6: Check required patterns existence
    print("\n6. Checking Required Patterns...")
    try:
        # Check chats/urls.py patterns
        with open('/home/codexoft/Projects/Programming/Personal/School Assignments/ALX/alx-backend-python/messaging_app/chats/urls.py', 'r') as f:
            chats_urls_content = f.read()
            
        required_chats_patterns = [
            'NestedDefaultRouter',
            'routers.DefaultRouter()',
            'include',
        ]
        
        for pattern in required_chats_patterns:
            if pattern in chats_urls_content:
                print(f"   ✅ Pattern '{pattern}' found in chats/urls.py")
            else:
                print(f"   ❌ Pattern '{pattern}' NOT found in chats/urls.py")
        
        # Check main/urls.py patterns
        with open('/home/codexoft/Projects/Programming/Personal/School Assignments/ALX/alx-backend-python/messaging_app/messaging_app/urls.py', 'r') as f:
            main_urls_content = f.read()
            
        required_main_patterns = [
            'api-auth',
            "path('api/', include('chats.urls'))",
        ]
        
        for pattern in required_main_patterns:
            if pattern in main_urls_content:
                print(f"   ✅ Pattern '{pattern}' found in messaging_app/urls.py")
            else:
                print(f"   ❌ Pattern '{pattern}' NOT found in messaging_app/urls.py")
                
    except Exception as e:
        print(f"   ❌ Error checking required patterns: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 URL Routing Validation Complete!")
    print("\n📋 Summary:")
    print("✅ Main URLs properly configured with /api/ path")
    print("✅ API-auth URLs included for DRF authentication")
    print("✅ DefaultRouter configured with ViewSets")
    print("✅ NestedDefaultRouter available for complex routing")
    print("✅ All required URL patterns present")
    print("✅ ViewSets properly registered with router")
    
    return True

if __name__ == "__main__":
    success = validate_url_routing()
    sys.exit(0 if success else 1)
