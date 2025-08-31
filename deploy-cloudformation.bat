@echo off
echo 🚀 Deploying UAV Service Management Tool using CloudFormation...
echo.

REM Check prerequisites
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI is not installed
    pause
    exit /b 1
)

aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS credentials not configured
    pause
    exit /b 1
)

REM Get variables
for /f %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
set REGION=us-east-1
set STACK_NAME=uav-service-management-stack
set REPOSITORY_NAME=uav-service-management

echo 📦 Account ID: %ACCOUNT_ID%
echo 🌍 Region: %REGION%
echo 📚 Stack Name: %STACK_NAME%
echo.

REM First, build and push the Docker image
echo 🐳 Building and pushing Docker image...
call deploy-aws.bat

echo.
echo 🏗️ Deploying CloudFormation stack...

REM Deploy CloudFormation stack
aws cloudformation deploy ^
  --template-file aws-cloudformation/ecs-fargate.yaml ^
  --stack-name %STACK_NAME% ^
  --parameter-overrides ImageURI=%ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest ^
  --capabilities CAPABILITY_NAMED_IAM ^
  --region %REGION%

if %errorlevel% equ 0 (
    echo.
    echo ✅ CloudFormation deployment successful!
    echo.
    echo 🌐 Getting Load Balancer URL...
    for /f %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" --output text --region %REGION%') do set LB_URL=%%i
    echo.
    echo 🎉 Your UAV Service Management Tool is deployed!
    echo 🔗 Access your application at: %LB_URL%
    echo.
    echo ⏳ Note: It may take 2-3 minutes for the service to be fully available
    echo.
    echo 📊 Monitoring:
    echo - ECS Console: https://console.aws.amazon.com/ecs/
    echo - CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/
    echo.
) else (
    echo ❌ CloudFormation deployment failed
    echo Check the CloudFormation console for details
)

pause
