#!/bin/bash

# Script to deploy Django Messaging App on Kubernetes
set -e

echo "==============================================="
echo "Deploying Django Messaging App on Kubernetes"
echo "==============================================="

# Check if minikube is running
echo "🔍 Checking if minikube is running..."
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Starting minikube..."
    minikube start --driver=docker
else
    echo "✅ Minikube is running"
fi

# Configure Docker to use minikube's Docker daemon
echo "🐳 Configuring Docker to use minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image inside minikube
echo "🔨 Building Docker image for the Django app..."
docker build -t messaging-app:latest .

echo "📋 Listing Docker images..."
docker images | grep messaging-app

# Apply the Kubernetes deployment
echo "🚀 Applying Kubernetes deployment..."
kubectl apply -f deployment.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mysql-database
kubectl wait --for=condition=available --timeout=300s deployment/django-messaging-app

# Get deployment status
echo ""
echo "==============================================="
echo "Deployment Status"
echo "==============================================="
echo "📊 Deployments:"
kubectl get deployments

echo ""
echo "📦 Pods:"
kubectl get pods

echo ""
echo "🔗 Services:"
kubectl get services

echo ""
echo "==============================================="
echo "Pod Logs"
echo "==============================================="

# Get Django app pods and show logs
DJANGO_PODS=$(kubectl get pods -l app=django-messaging-app -o jsonpath='{.items[*].metadata.name}')
if [ -n "$DJANGO_PODS" ]; then
    for pod in $DJANGO_PODS; do
        echo "📋 Logs for Django pod: $pod"
        kubectl logs $pod --tail=20 || echo "No logs available yet"
        echo ""
    done
else
    echo "❌ No Django pods found"
fi

# Get MySQL pod and show logs
MYSQL_PODS=$(kubectl get pods -l app=mysql-database -o jsonpath='{.items[*].metadata.name}')
if [ -n "$MYSQL_PODS" ]; then
    for pod in $MYSQL_PODS; do
        echo "📋 Logs for MySQL pod: $pod"
        kubectl logs $pod --tail=20 || echo "No logs available yet"
        echo ""
    done
else
    echo "❌ No MySQL pods found"
fi

echo ""
echo "==============================================="
echo "Verification Commands"
echo "==============================================="
echo "To check pod status: kubectl get pods"
echo "To view pod logs: kubectl logs <pod-name>"
echo "To describe a pod: kubectl describe pod <pod-name>"
echo "To get services: kubectl get services"
echo "To port-forward to Django app: kubectl port-forward service/django-messaging-service 8000:8000"
echo ""
echo "✅ Deployment completed successfully!"
