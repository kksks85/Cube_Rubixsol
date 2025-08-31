@echo off
echo 🚀 Starting AWS deployment for UAV Service Management Tool...
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI is not installed. Please install it first.
    echo Download from: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check AWS credentials
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS credentials not configured. Run: aws configure
    pause
    exit /b 1
)

REM Get AWS account ID
for /f %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo ✅ AWS Account ID: %ACCOUNT_ID%

REM Variables
set REGION=us-east-1
set REPOSITORY_NAME=uav-service-management
set CLUSTER_NAME=uav-service-cluster
set SERVICE_NAME=uav-service

echo 📦 Building Docker image...
docker build -t %REPOSITORY_NAME% . || (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo 🏗️ Creating ECR repository...
aws ecr describe-repositories --repository-names %REPOSITORY_NAME% --region %REGION% >nul 2>&1 || (
    aws ecr create-repository --repository-name %REPOSITORY_NAME% --region %REGION%
    echo ✅ ECR repository created
)

echo 🔐 Logging into ECR...
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

echo 🏷️ Tagging image...
docker tag %REPOSITORY_NAME%:latest %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest

echo ⬆️ Pushing image to ECR...
docker push %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest

echo.
echo ✅ Docker image successfully pushed to ECR!
echo.
echo 📦 Image URI: %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest
echo.
echo 🎯 Next Steps:
echo 1. Go to AWS ECS Console: https://console.aws.amazon.com/ecs/
echo 2. Create a new cluster (if you don't have one)
echo 3. Create a task definition with the image URI above
echo 4. Create a service to run your application
echo.
echo 📚 For detailed instructions, see AWS_DEPLOYMENT_GUIDE.md
echo.
echo 💡 Quick ECS Setup:
echo - Task Memory: 2048 MB
echo - Task CPU: 1024 units
echo - Container Port: 5000
echo - Environment: FLASK_ENV=production
echo.

pause
