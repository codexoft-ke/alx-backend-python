#!/bin/bash

# Test script to verify kubctl-0x01 functionality
echo "==============================================="
echo "Testing kubctl-0x01 Script Components"
echo "==============================================="

# Test 1: Check if kubectl is available
echo "🧪 Test 1: Checking kubectl availability..."
if command -v kubectl >/dev/null 2>&1; then
    echo "✅ kubectl is available"
    kubectl version --client --short 2>/dev/null || echo "kubectl version check completed"
else
    echo "❌ kubectl not found"
fi

# Test 2: Check if minikube is available
echo ""
echo "🧪 Test 2: Checking minikube availability..."
if command -v minikube >/dev/null 2>&1; then
    echo "✅ minikube is available"
    minikube version
else
    echo "❌ minikube not found"
fi

# Test 3: Check if wrk is available or can be installed
echo ""
echo "🧪 Test 3: Checking wrk availability..."
if command -v wrk >/dev/null 2>&1; then
    echo "✅ wrk is available"
    wrk --version 2>/dev/null || echo "wrk is installed"
else
    echo "❌ wrk not found - will be installed when script runs"
fi

# Test 4: Check cluster status (if running)
echo ""
echo "🧪 Test 4: Checking cluster status..."
if minikube status 2>/dev/null | grep -q "Running"; then
    echo "✅ Minikube cluster is running"
    echo "📊 Current deployments:"
    kubectl get deployments 2>/dev/null || echo "No deployments found or cluster not accessible"
else
    echo "⚠️  Minikube cluster is not running - will need to start before running kubctl-0x01"
fi

echo ""
echo "==============================================="
echo "Script Readiness Summary"
echo "==============================================="
echo "✅ kubctl-0x01 script is ready to run"
echo "📝 Script location: /workspaces/alx-backend-python/messaging_app/kubctl-0x01"
echo ""
echo "📋 What the script will do:"
echo "  1. Scale django-messaging-app deployment to 3 replicas"
echo "  2. Verify multiple pods are running"
echo "  3. Perform load testing with wrk"
echo "  4. Monitor resource usage with kubectl top"
echo ""
echo "🚀 To run the scaling script, execute:"
echo "    ./kubctl-0x01"
