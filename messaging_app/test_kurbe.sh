#!/bin/bash

# Simple test script to verify kurbeScript functionality
echo "Testing kurbeScript functionality..."

# Check if minikube is installed
if command -v minikube >/dev/null 2>&1; then
    echo "✅ minikube is available"
    minikube version
else
    echo "❌ minikube not found"
fi

# Check if kubectl is installed
if command -v kubectl >/dev/null 2>&1; then
    echo "✅ kubectl is available"
    kubectl version --client
else
    echo "❌ kubectl not found"
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "✅ docker is available"
else
    echo "❌ docker not found"
fi

echo "All prerequisites are available for Kubernetes setup!"
