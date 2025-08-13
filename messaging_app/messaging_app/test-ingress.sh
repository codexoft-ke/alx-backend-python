#!/bin/bash

# test-ingress.sh - Test Ingress Configuration
# This script tests the Ingress setup and connectivity

echo "==============================================="
echo "Testing Kubernetes Ingress Configuration"
echo "==============================================="

# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo "🌐 Minikube IP: $MINIKUBE_IP"

# Check if Ingress exists
echo ""
echo "🔍 Checking Ingress resources..."
kubectl get ingress

# Test Ingress endpoints
echo ""
echo "🧪 Testing Ingress endpoints..."

# Test with Host headers
echo "Testing main app endpoint:"
curl -H "Host: messaging-app.local" -I http://$MINIKUBE_IP/ || echo "❌ Main app not accessible"

echo ""
echo "Testing admin endpoint:"
curl -H "Host: messaging-app.local" -I http://$MINIKUBE_IP/admin/ || echo "❌ Admin not accessible"

echo ""
echo "Testing API endpoint:"
curl -H "Host: messaging-app.local" -I http://$MINIKUBE_IP/api/ || echo "❌ API not accessible"

echo ""
echo "Testing API subdomain:"
curl -H "Host: api.messaging-app.local" -I http://$MINIKUBE_IP/ || echo "❌ API subdomain not accessible"

echo ""
echo "==============================================="
echo "Ingress Test Complete!"
echo "==============================================="
