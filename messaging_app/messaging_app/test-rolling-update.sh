#!/bin/bash

# test-rolling-update.sh - Test script for rolling update functionality

echo "==============================================="
echo "Testing Rolling Update Setup"
echo "==============================================="

# Check if required files exist
echo "🔍 Checking required files..."

if [ -f "/workspaces/alx-backend-python/messaging_app/messaging_app/blue_deployment.yaml" ]; then
    echo "✅ blue_deployment.yaml exists"
else
    echo "❌ blue_deployment.yaml not found"
fi

if [ -f "/workspaces/alx-backend-python/messaging_app/messaging_app/kubctl-0x03" ]; then
    echo "✅ kubctl-0x03 script exists"
else
    echo "❌ kubctl-0x03 script not found"
fi

# Check blue_deployment.yaml content
echo ""
echo "🔍 Checking blue_deployment.yaml content..."
if grep -q "messaging-app:2.0" "/workspaces/alx-backend-python/messaging_app/messaging_app/blue_deployment.yaml"; then
    echo "✅ Image version updated to 2.0"
else
    echo "❌ Image version not updated to 2.0"
fi

if grep -q "RollingUpdate" "/workspaces/alx-backend-python/messaging_app/messaging_app/blue_deployment.yaml"; then
    echo "✅ Rolling update strategy configured"
else
    echo "❌ Rolling update strategy not found"
fi

# Check script permissions
if [ -x "/workspaces/alx-backend-python/messaging_app/messaging_app/kubctl-0x03" ]; then
    echo "✅ kubctl-0x03 script is executable"
else
    echo "❌ kubctl-0x03 script is not executable"
fi

echo ""
echo "==============================================="
echo "Setup Verification Complete"
echo "==============================================="
echo ""
echo "To run the rolling update:"
echo "cd /workspaces/alx-backend-python/messaging_app/messaging_app"
echo "./kubctl-0x03"
