# Jenkins Docker Build Setup Guide

## Overview
This guide explains the extended Jenkins pipeline that builds and pushes Docker images for the Django messaging app.

## Jenkins Pipeline Features

### New Stages Added:
1. **Build Docker Image** - Builds the Docker image with version tags
2. **Push Docker Image** - Pushes the image to Docker Hub

### Environment Variables:
- `DOCKER_HUB_REPO`: Your Docker Hub repository (format: username/repository-name)
- `DOCKER_IMAGE_TAG`: Uses build number for unique versioning
- `DOCKER_LATEST_TAG`: Always tagged as 'latest'

## Prerequisites

### 1. Docker Hub Account
- Create an account at https://hub.docker.com
- Create a repository for your messaging app

### 2. Jenkins Credentials Setup

#### GitHub Credentials (if not already configured):
1. Go to Jenkins Dashboard → Manage Jenkins → Manage Credentials
2. Add new credential:
   - Kind: Username with password
   - ID: `github-credentials`
   - Username: Your GitHub username
   - Password: Your GitHub personal access token

#### Docker Hub Credentials:
1. Go to Jenkins Dashboard → Manage Jenkins → Manage Credentials
2. Add new credential:
   - Kind: Username with password
   - ID: `docker-hub-credentials`
   - Username: Your Docker Hub username
   - Password: Your Docker Hub password or access token

### 3. Jenkins Plugins Required
Ensure these plugins are installed:
- Docker Pipeline
- Docker Plugin
- Pipeline
- Git Plugin

## Configuration Steps

### 1. Update Docker Hub Repository Name
In the Jenkinsfile, replace:
```groovy
DOCKER_HUB_REPO = 'your-dockerhub-username/messaging-app'
```
With your actual Docker Hub username and desired repository name.

### 2. Jenkins Job Configuration
1. Create a new Pipeline job in Jenkins
2. Configure Source Code Management:
   - Repository URL: https://github.com/codexoft-ke/alx-backend-python.git
   - Branch: main
   - Credentials: github-credentials
3. Pipeline Definition: Pipeline script from SCM
4. Script Path: messaging_app/messaging_app/Jenkinsfile

## Pipeline Stages Workflow

1. **Checkout** - Clones the repository
2. **Setup Environment** - Creates Python virtual environment and installs dependencies
3. **Lint Code** - Runs flake8 code linting
4. **Database Setup** - Runs Django migrations
5. **Run Tests** - Executes pytest and Django tests
6. **Generate Reports** - Creates coverage and test reports
7. **Build Docker Image** - Builds Docker image with tags
8. **Push Docker Image** - Pushes image to Docker Hub

## Docker Image Tags

The pipeline creates two tags for each build:
- `your-repo:BUILD_NUMBER` - Unique version for each build
- `your-repo:latest` - Always points to the most recent build

## Monitoring and Troubleshooting

### Build Logs
Monitor the Jenkins build logs for:
- Docker build progress
- Image push confirmation
- Any error messages

### Common Issues and Solutions

1. **Docker Hub Login Fails**
   - Verify credentials are correct
   - Check if Docker Hub account is active
   - Ensure Docker Hub repository exists

2. **Docker Build Fails**
   - Check Dockerfile syntax
   - Verify all required files are in the repository
   - Ensure base image is accessible

3. **Docker Push Fails**
   - Check internet connectivity
   - Verify Docker Hub repository permissions
   - Ensure image was built successfully

## Post-Build Cleanup

The pipeline automatically:
- Removes local Docker images to save disk space
- Archives test results and coverage reports
- Provides success/failure notifications with Docker image details

## Manual Trigger

To manually trigger the pipeline:
1. Go to Jenkins Dashboard
2. Select your pipeline job
3. Click "Build Now"
4. Monitor the build progress in real-time

## Security Best Practices

1. Use Docker Hub access tokens instead of passwords
2. Regularly rotate credentials
3. Limit Docker Hub repository access permissions
4. Monitor build logs for sensitive information leaks

## Next Steps

After successful build and push:
1. Verify image is available on Docker Hub
2. Test pulling and running the image locally
3. Consider setting up automated deployment from the Docker image
4. Implement image vulnerability scanning
