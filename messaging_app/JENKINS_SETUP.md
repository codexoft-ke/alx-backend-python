# Jenkins CI/CD Pipeline Setup

This document provides instructions for setting up Jenkins in a Docker container and configuring a CI/CD pipeline for the Django messaging application.

## Prerequisites

- Docker installed and running
- Access to GitHub repository
- Basic understanding of Jenkins and CI/CD concepts

## Jenkins Setup

### 1. Run Jenkins in Docker Container

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

This command will:
- Pull the latest Long-Term Support (LTS) Jenkins image
- Expose Jenkins on port 8080
- Map the Jenkins home directory to the host machine to persist data
- Run Jenkins as a background daemon

### 2. Access Jenkins Dashboard

1. Open your browser and navigate to `http://localhost:8080`
2. Get the initial admin password:
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Use the password: `9bf53a1881124d34a9a5ebb9f08ff87e`
4. Follow the setup wizard to install suggested plugins

### 3. Install Required Plugins

Install the following plugins in Jenkins:
- **Git Plugin**: For source code management
- **Pipeline Plugin**: For pipeline as code functionality
- **ShiningPanda Plugin**: For Python environment management
- **HTML Publisher Plugin**: For publishing HTML reports
- **JUnit Plugin**: For test result publishing
- **Coverage Plugin**: For code coverage reports

To install plugins:
1. Go to "Manage Jenkins" → "Manage Plugins"
2. Click on "Available" tab
3. Search for each plugin and install

### 4. Configure GitHub Credentials

1. Go to "Manage Jenkins" → "Manage Credentials"
2. Click on "Jenkins" under "Stores scoped to Jenkins"
3. Click "Global credentials"
4. Click "Add Credentials"
5. Select "Username with password"
6. Enter your GitHub username and personal access token
7. Set ID as "github-credentials"

## Pipeline Configuration

### 1. Create New Pipeline Job

1. Click "New Item" on Jenkins dashboard
2. Enter job name: "messaging-app-ci"
3. Select "Pipeline" and click OK

### 2. Configure Pipeline

1. In the job configuration:
   - **General**: Add description
   - **Build Triggers**: Check "GitHub hook trigger for GITScm polling"
   - **Pipeline**: 
     - Definition: "Pipeline script from SCM"
     - SCM: Git
     - Repository URL: `https://github.com/codexoft-ke/alx-backend-python.git`
     - Credentials: Select your GitHub credentials
     - Branch: `*/main`
     - Script Path: `messaging_app/Jenkinsfile`

### 3. Pipeline Features

The Jenkinsfile includes the following stages:

1. **Checkout**: Pulls source code from GitHub
2. **Setup Environment**: Creates Python virtual environment and installs dependencies
3. **Lint Code**: Runs flake8 for code quality checks
4. **Database Setup**: Runs Django migrations for testing
5. **Run Tests**: Executes pytest with coverage reporting
6. **Generate Reports**: Creates test and coverage reports

### 4. Generated Reports

The pipeline generates several reports:
- **Test Results**: JUnit XML format for test results
- **Coverage Report**: HTML and XML coverage reports
- **Lint Report**: flake8 code quality report

## Pipeline Execution

### Manual Trigger
1. Go to your pipeline job
2. Click "Build Now"
3. Monitor the build progress in "Build History"

### Automatic Trigger
Configure GitHub webhooks to trigger builds on code push:
1. In GitHub repository settings, go to "Webhooks"
2. Add webhook URL: `http://your-jenkins-url:8080/github-webhook/`
3. Select "Just the push event"

## Dependencies

### Production Dependencies
- Django==5.2.4
- djangorestframework==3.16.0
- django-filter==24.3
- drf-nested-routers==0.94.2
- requests==2.32.3
- gunicorn==23.0.0
- mysqlclient==2.2.4

### Development Dependencies
- pytest==8.3.3
- pytest-django==4.9.0
- pytest-cov==5.0.0
- coverage==7.6.1
- flake8==7.1.1
- factory-boy==3.3.1
- faker==30.3.0

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure Docker has proper permissions
2. **Port Conflicts**: Make sure ports 8080 and 50000 are available
3. **Plugin Installation Failed**: Check internet connectivity and Jenkins logs
4. **Test Failures**: Review test logs and ensure database migrations are successful

### Viewing Logs

```bash
# View Jenkins container logs
docker logs jenkins

# Access Jenkins container shell
docker exec -it jenkins bash
```

## Security Considerations

1. Change default admin password after setup
2. Use personal access tokens instead of passwords for GitHub
3. Regularly update Jenkins and plugins
4. Implement proper user roles and permissions
5. Use HTTPS in production environments

## Next Steps

1. Add Docker image building to the pipeline
2. Integrate with Docker Hub for image storage
3. Set up GitHub Actions for additional CI/CD workflows
4. Add security scanning tools (e.g., Snyk, Trivy)
5. Implement deployment to staging/production environments
