# GitHub Actions CI/CD Setup for Django Messaging App

This repository includes comprehensive GitHub Actions workflows for continuous integration and testing of the Django messaging application.

## 🚀 Workflows Overview

### 1. Main CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Only when files in `messaging_app/` directory or workflow files change

**Features:**
- **Multi-Python Version Testing**: Tests against Python 3.10.12, 3.11, and 3.12
- **MySQL Database Service**: Uses MySQL 8.0 with proper health checks
- **Comprehensive Testing**: Runs both pytest and Django built-in tests
- **Code Quality**: Includes linting with flake8, Black, and isort
- **Security Scanning**: Bandit for security vulnerabilities, Safety for dependency security
- **Coverage Reports**: Generates coverage reports and uploads to Codecov
- **Artifact Storage**: Saves test results and coverage reports

### 2. Integration & Performance Tests (`.github/workflows/integration.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch
- Scheduled daily runs at 2 AM UTC

**Features:**
- **Extended Services**: MySQL + Redis for comprehensive testing
- **Integration Testing**: Runs tests marked with `@pytest.mark.integration`
- **Performance Benchmarks**: Uses pytest-benchmark for performance testing
- **API Testing**: Validates API endpoints functionality
- **Load Testing**: Includes Locust for load testing capabilities

## 🛠 Configuration Details

### Database Configuration

The workflows use MySQL 8.0 with the following configuration:
```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: root_password_123
      MYSQL_DATABASE: messaging_app_test_db
      MYSQL_USER: messaging_user
      MYSQL_PASSWORD: messaging_password_123
    ports:
      - 3306:3306
```

### Environment Variables

Key environment variables used in the workflows:
- `DJANGO_SETTINGS_MODULE`: `messaging_app.settings`
- `MYSQL_DATABASE`: Test database name
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database password
- `DB_HOST`: Database host (127.0.0.1)
- `DB_PORT`: Database port (3306)
- `SECRET_KEY`: Django secret key for testing

### Python Dependencies

The workflows install dependencies from:
- `messaging_app/requirements.txt` - Production dependencies
- `messaging_app/requirements-dev.txt` - Development and testing dependencies

Additional testing tools installed:
- `pytest-benchmark` - Performance testing
- `locust` - Load testing
- `bandit` - Security linting
- `safety` - Dependency security checking
- `black` - Code formatting
- `isort` - Import sorting

## 📊 Test Jobs Breakdown

### 1. Test Job (Main CI)
- **Setup**: Python environment, dependencies, MySQL
- **Database**: Migration and connection verification
- **Linting**: flake8 code quality checks
- **Testing**: pytest and Django test suite
- **Coverage**: Code coverage analysis and reporting
- **Artifacts**: Test results and coverage reports

### 2. Lint Job (Code Quality)
- **Black**: Code formatting verification
- **isort**: Import statement organization
- **flake8**: PEP 8 compliance and code quality

### 3. Security Job (Security Scanning)
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency security analysis
- **Reports**: JSON security reports as artifacts

### 4. Integration Tests Job
- **Services**: MySQL + Redis setup
- **Integration**: Comprehensive API and database testing
- **Performance**: Basic performance benchmarks
- **Load Data**: Test fixtures and sample data

### 5. Performance Tests Job
- **Benchmarking**: Performance measurement with pytest-benchmark
- **Load Testing**: Capacity and stress testing preparation
- **Server Testing**: Live Django server testing

## 📈 Monitoring and Reports

### Artifacts Generated
- **Test Results**: JUnit XML format for test reporting
- **Coverage Reports**: XML and HTML coverage reports
- **Security Reports**: JSON security scan results
- **Performance Data**: Benchmark results in JSON format

### Codecov Integration
Coverage reports are automatically uploaded to Codecov for:
- Coverage tracking over time
- Pull request coverage analysis
- Coverage badges and reporting

## 🔧 Local Development

To run tests locally with the same configuration:

```bash
# Install dependencies
pip install -r messaging_app/requirements.txt
pip install -r messaging_app/requirements-dev.txt

# Set up MySQL database
mysql -u root -p -e "CREATE DATABASE messaging_app_test_db;"
mysql -u root -p -e "CREATE USER 'messaging_user'@'localhost' IDENTIFIED BY 'messaging_password_123';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON messaging_app_test_db.* TO 'messaging_user'@'localhost';"

# Run migrations
cd messaging_app
python manage.py migrate

# Run tests
python -m pytest test_*.py -v --cov=.
python manage.py test

# Run linting
flake8 --max-line-length=88 --exclude=venv,migrations,__pycache__,.git .
black --check .
isort --check-only .

# Security scanning
bandit -r . -x tests/
safety check
```

## 🚦 Status Badges

Add these badges to your repository README:

```markdown
![CI](https://github.com/codexoft-ke/alx-backend-python/workflows/Django%20CI/badge.svg)
![Integration Tests](https://github.com/codexoft-ke/alx-backend-python/workflows/Integration%20%26%20Performance%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/codexoft-ke/alx-backend-python/branch/main/graph/badge.svg)](https://codecov.io/gh/codexoft-ke/alx-backend-python)
```

## 🛡 Security Considerations

- Secrets are managed through GitHub repository settings
- Database credentials are environment-specific
- Security scanning runs on every push
- Dependency vulnerability checking included

## 📝 Customization

### Adding New Test Types
To add new test categories, use pytest markers:

```python
import pytest

@pytest.mark.integration
def test_api_integration():
    pass

@pytest.mark.slow
def test_long_running_process():
    pass

@pytest.mark.benchmark
def test_performance_benchmark():
    pass
```

### Modifying Database Configuration
Update the MySQL service configuration in the workflow files to match your requirements:
- Change database name, user, or password
- Modify MySQL version
- Add additional database configurations

### Adding New Services
Add additional services like Redis, Elasticsearch, etc., in the `services` section:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - 6379:6379
    options: >-
      --health-cmd="redis-cli ping"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=5
```

## 🔍 Troubleshooting

### Common Issues

1. **MySQL Connection Failures**
   - Check health check configuration
   - Verify credentials match between service and environment variables
   - Ensure proper wait conditions before running tests

2. **Test Failures**
   - Review test logs in GitHub Actions
   - Check database migration status
   - Verify all required environment variables are set

3. **Coverage Issues**
   - Ensure pytest-cov is installed
   - Check coverage configuration in pytest.ini
   - Verify file paths in coverage reports

4. **Dependency Issues**
   - Keep requirements files updated
   - Check for version conflicts
   - Use pip cache for faster builds

### Getting Help

- Check GitHub Actions logs for detailed error messages
- Review the Django application logs
- Verify database connectivity and permissions
- Ensure all required environment variables are configured

This setup provides a robust, scalable CI/CD pipeline that ensures code quality, security, and functionality across multiple Python versions and testing scenarios.
