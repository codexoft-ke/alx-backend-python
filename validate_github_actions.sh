#!/bin/bash

# GitHub Actions Workflow Validation Script
# This script validates the CI workflow configuration

set -e

echo "🔍 Validating GitHub Actions Workflow Setup..."

# Check if workflow files exist
WORKFLOW_DIR=".github/workflows"
CI_WORKFLOW="$WORKFLOW_DIR/ci.yml"
INTEGRATION_WORKFLOW="$WORKFLOW_DIR/integration.yml"

if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ GitHub workflows directory not found: $WORKFLOW_DIR"
    exit 1
fi

if [ ! -f "$CI_WORKFLOW" ]; then
    echo "❌ Main CI workflow not found: $CI_WORKFLOW"
    exit 1
fi

if [ ! -f "$INTEGRATION_WORKFLOW" ]; then
    echo "❌ Integration workflow not found: $INTEGRATION_WORKFLOW"
    exit 1
fi

echo "✅ Workflow files found"

# Check if messaging_app directory exists
if [ ! -d "messaging_app" ]; then
    echo "❌ messaging_app directory not found"
    exit 1
fi

echo "✅ messaging_app directory found"

# Check if requirements files exist
REQUIREMENTS="messaging_app/requirements.txt"
DEV_REQUIREMENTS="messaging_app/requirements-dev.txt"

if [ ! -f "$REQUIREMENTS" ]; then
    echo "❌ Requirements file not found: $REQUIREMENTS"
    exit 1
fi

if [ ! -f "$DEV_REQUIREMENTS" ]; then
    echo "❌ Dev requirements file not found: $DEV_REQUIREMENTS"
    exit 1
fi

echo "✅ Requirements files found"

# Check if Django manage.py exists
MANAGE_PY="messaging_app/manage.py"
if [ ! -f "$MANAGE_PY" ]; then
    echo "❌ Django manage.py not found: $MANAGE_PY"
    exit 1
fi

echo "✅ Django manage.py found"

# Check if test files exist
TEST_FILES=$(find messaging_app -name "test_*.py" -type f)
if [ -z "$TEST_FILES" ]; then
    echo "⚠️  No test files found (test_*.py)"
else
    echo "✅ Test files found:"
    echo "$TEST_FILES" | sed 's/^/    /'
fi

# Check if pytest.ini exists
PYTEST_INI="messaging_app/pytest.ini"
if [ ! -f "$PYTEST_INI" ]; then
    echo "⚠️  pytest.ini not found: $PYTEST_INI"
else
    echo "✅ pytest.ini found"
fi

# Validate YAML syntax (if yamllint is available)
if command -v yamllint >/dev/null 2>&1; then
    echo "🔍 Validating YAML syntax..."
    yamllint "$CI_WORKFLOW" || echo "⚠️  YAML syntax issues in $CI_WORKFLOW"
    yamllint "$INTEGRATION_WORKFLOW" || echo "⚠️  YAML syntax issues in $INTEGRATION_WORKFLOW"
    echo "✅ YAML syntax validation completed"
else
    echo "⚠️  yamllint not found, skipping YAML syntax validation"
fi

# Check workflow triggers
echo "🔍 Checking workflow triggers..."
if grep -q "on:" "$CI_WORKFLOW"; then
    echo "✅ CI workflow has triggers configured"
else
    echo "❌ CI workflow missing triggers"
    exit 1
fi

# Check for required jobs
echo "🔍 Checking required jobs..."
REQUIRED_JOBS=("test" "lint" "security")
for job in "${REQUIRED_JOBS[@]}"; do
    if grep -q "^  $job:" "$CI_WORKFLOW"; then
        echo "✅ Job '$job' found in CI workflow"
    else
        echo "❌ Job '$job' missing in CI workflow"
        exit 1
    fi
done

# Check MySQL service configuration
echo "🔍 Checking MySQL service configuration..."
if grep -q "mysql:" "$CI_WORKFLOW"; then
    echo "✅ MySQL service configured in CI workflow"
else
    echo "❌ MySQL service missing in CI workflow"
    exit 1
fi

# Check Python version matrix
echo "🔍 Checking Python version matrix..."
if grep -q "python-version:" "$CI_WORKFLOW"; then
    echo "✅ Python version matrix configured"
else
    echo "❌ Python version matrix missing"
    exit 1
fi

# Check environment variables
echo "🔍 Checking environment variables..."
REQUIRED_ENV_VARS=("DJANGO_SETTINGS_MODULE" "MYSQL_DATABASE" "MYSQL_USER" "MYSQL_PASSWORD")
for env_var in "${REQUIRED_ENV_VARS[@]}"; do
    if grep -q "$env_var" "$CI_WORKFLOW"; then
        echo "✅ Environment variable '$env_var' found"
    else
        echo "❌ Environment variable '$env_var' missing"
        exit 1
    fi
done

echo ""
echo "🎉 GitHub Actions workflow validation completed successfully!"
echo ""
echo "📋 Summary:"
echo "   ✅ Workflow files are properly configured"
echo "   ✅ Django application structure is correct"
echo "   ✅ Required jobs and services are configured"
echo "   ✅ Environment variables are set"
echo ""
echo "🚀 Next steps:"
echo "   1. Commit and push the workflow files to your repository"
echo "   2. Create a pull request to trigger the first workflow run"
echo "   3. Monitor the GitHub Actions tab for build results"
echo "   4. Set up Codecov integration for coverage reporting"
echo ""
echo "💡 Tips:"
echo "   - Add a .codecov.yml file for custom coverage configuration"
echo "   - Consider adding status badges to your README.md"
echo "   - Set up branch protection rules requiring CI checks"
