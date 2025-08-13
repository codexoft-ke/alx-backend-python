#!/bin/bash

# setup-ingress.sh - Kubernetes Ingress Setup Script
# This script installs Nginx Ingress controller and applies Ingress configuration

set -e  # Exit on any error

echo "==============================================="
echo "Kubernetes Ingress Setup for Django Messaging App"
echo "==============================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if minikube is available
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube not found. Please install minikube first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible. Please start minikube first."
    exit 1
fi

echo "✅ Prerequisites checked"

echo ""
echo "==============================================="
echo "1. Installing Nginx Ingress Controller"
echo "==============================================="

# Enable Ingress addon in minikube
echo "🔧 Enabling Nginx Ingress controller in minikube..."
minikube addons enable ingress

echo "⏳ Waiting for Ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s || echo "⚠️ Timeout waiting for ingress controller, proceeding anyway..."

# Verify Ingress controller is running
echo ""
echo "📊 Ingress controller status:"
kubectl get pods -n ingress-nginx

echo ""
echo "==============================================="
echo "2. Applying Ingress Configuration"
echo "==============================================="

# Apply the Ingress resource
echo "🚀 Applying Ingress configuration..."
kubectl apply -f ingress.yaml

echo "⏳ Waiting for Ingress to be ready..."
sleep 10

echo ""
echo "📊 Ingress resources:"
kubectl get ingress

echo ""
echo "📋 Detailed Ingress information:"
kubectl describe ingress django-messaging-ingress

echo ""
echo "==============================================="
echo "3. Setting up Local DNS Resolution"
echo "==============================================="

# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo "🌐 Minikube IP: $MINIKUBE_IP"

# Create hosts entries for local testing
echo ""
echo "📝 To test the Ingress locally, add these entries to your /etc/hosts file:"
echo "$MINIKUBE_IP messaging-app.local"
echo "$MINIKUBE_IP api.messaging-app.local"
echo "$MINIKUBE_IP db.messaging-app.local"

# Enable Ingress DNS addon for automatic domain resolution
echo ""
echo "🔧 Enabling Ingress DNS addon..."
minikube addons enable ingress-dns || echo "⚠️ Ingress DNS addon not available or already enabled"

echo ""
echo "==============================================="
echo "4. Verifying Setup"
echo "==============================================="

# Check all services
echo "🔗 Current services:"
kubectl get services

echo ""
echo "🌐 Current ingresses:"
kubectl get ingress

echo ""
echo "📊 Ingress controller service:"
kubectl get service -n ingress-nginx

echo ""
echo "==============================================="
echo "5. Testing Connectivity"
echo "==============================================="

# Test if the service is accessible through Ingress
echo "🧪 Testing Ingress connectivity..."

# Wait a bit more for everything to be ready
sleep 5

# Test direct connection to the service first
echo "Testing direct service connection..."
kubectl port-forward service/django-messaging-service 8080:8000 &
PORT_FORWARD_PID=$!
sleep 3

# Test if port forwarding works
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/admin/ | grep -q "200\|302\|404"; then
    echo "✅ Service is accessible via port-forward"
else
    echo "⚠️ Service might not be ready yet"
fi

# Clean up port forwarding
kill $PORT_FORWARD_PID 2>/dev/null || true

# Test Ingress access (this requires /etc/hosts setup)
echo ""
echo "🌐 To test Ingress access, run these commands after updating /etc/hosts:"
echo "curl -H 'Host: messaging-app.local' http://$MINIKUBE_IP/admin/"
echo "curl -H 'Host: api.messaging-app.local' http://$MINIKUBE_IP/"

echo ""
echo "==============================================="
echo "Setup Complete!"
echo "==============================================="
echo "✅ Nginx Ingress controller installed"
echo "✅ Ingress resource created"
echo "✅ Domain routing configured"
echo ""
echo "📋 Available endpoints:"
echo "  - http://messaging-app.local/ (Main app)"
echo "  - http://messaging-app.local/admin/ (Django admin)"
echo "  - http://messaging-app.local/api/ (API endpoints)"
echo "  - http://api.messaging-app.local/ (API subdomain)"
echo ""
echo "🔧 Useful commands:"
echo "  - kubectl get ingress                    # Check Ingress status"
echo "  - kubectl describe ingress django-messaging-ingress  # Detailed info"
echo "  - minikube tunnel                       # Enable LoadBalancer access"
echo "  - kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx  # Check logs"
echo ""
echo "⚠️  Remember to update /etc/hosts with the displayed entries for local testing!"
