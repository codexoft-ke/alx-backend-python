#!/usr/bin/env python3
"""
Quick API test script to verify endpoints are working
Run this after starting the Django server
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser1",
    "password": "testpass123"
}

def test_api():
    """Run basic API tests"""
    print("🚀 Starting API tests...")
    
    # Test 1: Health check (no auth required)
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running on localhost:8000")
        return False
    
    # Test 2: JWT Authentication
    print("\n2. Testing JWT authentication...")
    try:
        auth_response = requests.post(
            f"{BASE_URL}/api/token/",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if auth_response.status_code == 200:
            tokens = auth_response.json()
            access_token = tokens.get('access')
            print("✅ JWT authentication successful")
            
            # Test 3: Authenticated request
            print("\n3. Testing authenticated request...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            user_response = requests.get(
                f"{BASE_URL}/api/users/me/",
                headers=headers
            )
            
            if user_response.status_code == 200:
                print("✅ Authenticated request successful")
                user_data = user_response.json()
                print(f"   User: {user_data.get('username')}")
            else:
                print(f"❌ Authenticated request failed: {user_response.status_code}")
                
        else:
            print(f"❌ JWT authentication failed: {auth_response.status_code}")
            print(f"   Response: {auth_response.text}")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
    
    # Test 4: Unauthorized access
    print("\n4. Testing unauthorized access protection...")
    try:
        unauth_response = requests.get(f"{BASE_URL}/api/conversations/")
        if unauth_response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
        else:
            print(f"❌ Unauthorized access not blocked: {unauth_response.status_code}")
    except Exception as e:
        print(f"❌ Unauthorized access test failed: {str(e)}")
    
    # Test 5: Pagination test
    print("\n5. Testing pagination...")
    try:
        if 'access_token' in locals():
            headers = {"Authorization": f"Bearer {access_token}"}
            paginated_response = requests.get(
                f"{BASE_URL}/api/messages/",
                headers=headers
            )
            
            if paginated_response.status_code == 200:
                data = paginated_response.json()
                if 'count' in data and 'results' in data:
                    print("✅ Pagination working correctly")
                    print(f"   Total messages: {data.get('count', 0)}")
                else:
                    print("❌ Pagination format incorrect")
            else:
                print(f"❌ Pagination test failed: {paginated_response.status_code}")
    except Exception as e:
        print(f"❌ Pagination test failed: {str(e)}")
    
    print("\n🎉 API tests completed!")
    print("\n📋 Next steps:")
    print("1. Import post_man-Collections/post_man-Collections.json into Postman")
    print("2. Set up environment variables in Postman")
    print("3. Create test users if they don't exist")
    print("4. Run the full test suite using the Postman collection")

if __name__ == "__main__":
    test_api()
