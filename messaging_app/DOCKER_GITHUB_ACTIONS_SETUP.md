# GitHub Actions Docker Build and Deploy Setup Guide

## Overview
This guide explains how to set up the GitHub Actions workflow (`dep.yml`) for building and pushing Docker images to Docker Hub with secure credential management.

## Workflow File Location
- **Path**: `messaging_app/.github/workflows/dep.yml`
- **Purpose**: Build, push, and deploy Docker images automatically

## Prerequisites

### 1. Docker Hub Account Setup
1. Create account at https://hub.docker.com
2. Create a repository for your messaging app
3. Generate an access token (recommended over password)

#### To Generate Docker Hub Access Token:
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Name: `github-actions-token`
4. Permissions: Read, Write, Delete
5. Copy the generated token (save it securely)

### 2. GitHub Secrets Configuration

#### Required Secrets:
Navigate to your GitHub repository → Settings → Secrets and variables → Actions

Add these repository secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DOCKER_HUB_USERNAME` | Your Docker Hub username | `yourusername` |
| `DOCKER_HUB_ACCESS_TOKEN` | Docker Hub access token | `dckr_pat_xyz123...` |

#### Steps to Add Secrets:
1. Go to GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret:
   - Name: `DOCKER_HUB_USERNAME`
   - Secret: Your Docker Hub username
   - Click **Add secret**
   - Repeat for `DOCKER_HUB_ACCESS_TOKEN`

## Workflow Features

### 🚀 **Automatic Triggers**
- **Push to main/develop**: Builds and deploys images
- **Pull Requests**: Builds images for testing
- **Releases**: Creates version-tagged images

### 🏗️ **Build Process**
1. **Multi-platform builds** using Docker Buildx
2. **Layer caching** for faster builds
3. **Metadata extraction** for proper tagging
4. **Build arguments** including version information

### 🔖 **Image Tagging Strategy**
- `latest` - Latest main branch build
- `main-{sha}` - Specific commit from main
- `develop-{sha}` - Specific commit from develop
- `pr-{number}` - Pull request builds
- `v1.0.0` - Semantic version tags (on releases)

### 🔒 **Security Features**
- **Trivy vulnerability scanning** after image build
- **SARIF upload** to GitHub Security tab
- **Secure credential handling** with GitHub Secrets

### 🚀 **Deployment Stages**
- **Staging**: Auto-deploy from develop branch
- **Production**: Auto-deploy from main branch
- **Environment protection** rules can be configured

## Workflow Jobs Breakdown

### 1. `build-and-push`
**Purpose**: Build and push Docker images to Docker Hub

**Steps**:
- Checkout source code
- Set up Docker Buildx for advanced features
- Login to Docker Hub using secrets
- Extract metadata for proper tagging
- Build and push multi-platform images
- Generate deployment summary

**Caching**: Uses GitHub Actions cache for Docker layers

### 2. `security-scan`
**Purpose**: Scan built images for vulnerabilities

**Features**:
- Trivy vulnerability scanner
- Upload results to GitHub Security tab
- Artifact upload for manual review
- Only runs on non-PR events

### 3. `deploy-staging`
**Purpose**: Deploy to staging environment

**Conditions**:
- Only runs on `develop` branch pushes
- Requires successful build and security scan
- Uses GitHub environment protection

### 4. `deploy-production`
**Purpose**: Deploy to production environment

**Conditions**:
- Only runs on `main` branch pushes
- Requires successful build and security scan
- Uses GitHub environment protection

### 5. `cleanup`
**Purpose**: Clean up resources after deployment

**Features**:
- Always runs regardless of other job status
- Can include cleanup of old images or artifacts

## Usage Instructions

### 1. Initial Setup
```bash
# 1. Configure GitHub Secrets (done via web interface)
# 2. Update Docker Hub repository name if needed in workflow file
# 3. Commit and push the workflow file

git add messaging_app/.github/workflows/dep.yml
git commit -m "Add Docker build and deploy workflow"
git push origin main
```

### 2. Trigger Builds

#### Automatic Triggers:
- **Push to main**: Builds and deploys to production
- **Push to develop**: Builds and deploys to staging
- **Create PR**: Builds image for testing
- **Create release**: Builds tagged version

#### Manual Trigger:
1. Go to GitHub repository → Actions tab
2. Select "Docker Build and Deploy" workflow
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

### 3. Monitor Builds
1. **Actions Tab**: View workflow progress
2. **Security Tab**: Review vulnerability scans
3. **Packages Tab**: See published Docker images
4. **Environment Tab**: Track deployments

## Environment Configuration

### GitHub Environments (Optional)
Set up environment protection rules:

1. Go to repository → Settings → Environments
2. Create environments: `staging`, `production`
3. Configure protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches

### Deployment Commands
Update deployment steps in the workflow:

```yaml
# For Kubernetes
- name: Deploy to production
  run: |
    kubectl set image deployment/messaging-app messaging-app=${{ env.DOCKER_HUB_REPO }}:latest

# For Docker Compose
- name: Deploy to production
  run: |
    docker-compose pull
    docker-compose up -d
```

## Image Usage

### Pull Latest Image
```bash
docker pull yourusername/messaging-app:latest
```

### Run Container
```bash
docker run -d \
  --name messaging-app \
  -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  yourusername/messaging-app:latest
```

### Use in Docker Compose
```yaml
services:
  web:
    image: yourusername/messaging-app:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/dbname
```

## Troubleshooting

### Common Issues

#### 1. Docker Hub Login Fails
```
Error: Login failed
```
**Solutions**:
- Verify `DOCKER_HUB_USERNAME` secret is correct
- Ensure `DOCKER_HUB_ACCESS_TOKEN` is valid
- Check if Docker Hub account is active

#### 2. Image Push Fails
```
Error: Failed to push image
```
**Solutions**:
- Verify repository exists on Docker Hub
- Check repository permissions
- Ensure access token has write permissions

#### 3. Build Context Issues
```
Error: Cannot find Dockerfile
```
**Solutions**:
- Verify Dockerfile exists in `messaging_app/` directory
- Check file path in workflow configuration
- Ensure proper repository structure

#### 4. Security Scan Failures
```
Error: Trivy scan failed
```
**Solutions**:
- Review vulnerability report
- Update base image or dependencies
- Consider suppressing non-critical issues

### Debug Information

#### View Build Logs
1. Go to Actions tab
2. Click on workflow run
3. Click on specific job
4. Expand step to view detailed logs

#### Download Artifacts
1. Go to completed workflow run
2. Scroll to "Artifacts" section
3. Download security scan results or other artifacts

## Security Best Practices

### 1. Secrets Management
- ✅ Use access tokens instead of passwords
- ✅ Rotate tokens regularly
- ✅ Use least privilege principle
- ✅ Never commit secrets to repository

### 2. Image Security
- ✅ Use official base images
- ✅ Regularly update dependencies
- ✅ Scan for vulnerabilities
- ✅ Use multi-stage builds to reduce attack surface

### 3. Access Control
- ✅ Configure environment protection rules
- ✅ Require reviews for production deployments
- ✅ Use branch protection rules
- ✅ Monitor deployment activities

## Monitoring and Alerts

### GitHub Notifications
- ✅ Workflow failures send email notifications
- ✅ Security alerts for vulnerabilities
- ✅ Pull request status checks

### Docker Hub Monitoring
- ✅ Monitor pull statistics
- ✅ Review security scan results
- ✅ Track image usage across environments

## Performance Optimization

### Build Speed
- ✅ Docker layer caching enabled
- ✅ Multi-stage builds for smaller images
- ✅ Parallel job execution where possible

### Resource Usage
- ✅ Efficient use of GitHub Actions minutes
- ✅ Conditional job execution
- ✅ Artifact cleanup to save storage

## Integration with Other Tools

### CI/CD Pipeline
- **GitHub Actions CI** (testing) → **GitHub Actions Deploy** (Docker)
- **Jenkins** (alternative CI) → **GitHub Actions Deploy** (Docker)

### Monitoring Tools
- **Prometheus**: Monitor container metrics
- **Grafana**: Visualize deployment data
- **Sentry**: Application error tracking

This setup provides a complete CI/CD pipeline for Docker image management, from build to deployment, with security and monitoring built-in.
