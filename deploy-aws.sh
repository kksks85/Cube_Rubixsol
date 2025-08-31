#!/bin/bash
set -e

echo "🚀 Starting AWS deployment for UAV Service Management Tool..."
echo

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run: aws configure"
    exit 1
fi

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account ID: $ACCOUNT_ID"

# Variables
REGION="us-east-1"
REPOSITORY_NAME="uav-service-management"
CLUSTER_NAME="uav-service-cluster"
SERVICE_NAME="uav-service"

echo "📦 Building Docker image..."
docker build -t $REPOSITORY_NAME . || {
    echo "❌ Docker build failed"
    exit 1
}

echo "🏗️ Creating ECR repository..."
aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $REGION > /dev/null 2>&1 || {
    aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION
    echo "✅ ECR repository created"
}

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "🏷️ Tagging image..."
docker tag $REPOSITORY_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest

echo "⬆️ Pushing image to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest

echo
echo "✅ Docker image successfully pushed to ECR!"
echo
echo "📦 Image URI: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest"
echo
echo "🎯 Next Steps:"
echo "1. Go to AWS ECS Console: https://console.aws.amazon.com/ecs/"
echo "2. Create a new cluster (if you don't have one)"
echo "3. Create a task definition with the image URI above"
echo "4. Create a service to run your application"
echo
echo "📚 For detailed instructions, see AWS_DEPLOYMENT_GUIDE.md"
echo
echo "💡 Quick ECS Setup:"
echo "- Task Memory: 2048 MB"
echo "- Task CPU: 1024 units"
echo "- Container Port: 5000"
echo "- Environment: FLASK_ENV=production"
echo
