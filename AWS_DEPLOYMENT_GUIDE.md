# AWS Deployment Guide for UAV Service Management Tool

## 🚀 AWS Deployment Options

We'll deploy using **AWS ECS Fargate** - the easiest and most scalable option for containerized applications.

---

## 📋 Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed and configured
3. **Docker Desktop** running
4. **IAM User** with appropriate permissions

---

## 🔧 Step 1: Install and Configure AWS CLI

### Install AWS CLI
```bash
# Windows (using Chocolatey)
choco install awscli

# Or download from: https://aws.amazon.com/cli/
```

### Configure AWS CLI
```bash
aws configure
```
Enter your:
- **AWS Access Key ID**: (from IAM user)
- **AWS Secret Access Key**: (from IAM user)
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

---

## 🏗️ Step 2: Build and Push Docker Image to ECR

### Create ECR Repository
```bash
# Create repository
aws ecr create-repository --repository-name uav-service-management --region us-east-1

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Build and Push Image
```bash
# Build image
docker build -t uav-service-management .

# Tag for ECR
docker tag uav-service-management:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/uav-service-management:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/uav-service-management:latest
```

---

## ☁️ Step 3: Deploy with ECS Fargate

### Option A: Using AWS Console (Recommended for beginners)

1. **Go to ECS Console**: https://console.aws.amazon.com/ecs/
2. **Create Cluster**:
   - Click "Create Cluster"
   - Choose "Networking only" (Fargate)
   - Name: `uav-service-cluster`
   - Create VPC or use default

3. **Create Task Definition**:
   - Click "Task Definitions" → "Create new Task Definition"
   - Choose "Fargate"
   - Task Definition Name: `uav-service-task`
   - Task Role: `ecsTaskExecutionRole`
   - Task Memory: `2048 MB`
   - Task CPU: `1024 units`

4. **Add Container**:
   - Container Name: `uav-service-container`
   - Image: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/uav-service-management:latest`
   - Memory Limits: `2048 MB`
   - Port Mappings: `5000:5000`
   - Environment Variables:
     - `FLASK_ENV=production`
     - `FLASK_HOST=0.0.0.0`
     - `FLASK_PORT=5000`

5. **Create Service**:
   - Go to your cluster → "Services" → "Create"
   - Launch Type: "Fargate"
   - Task Definition: `uav-service-task`
   - Service Name: `uav-service`
   - Desired Count: `1`
   - VPC: Select your VPC
   - Subnets: Select public subnets
   - Security Group: Allow inbound on port 5000
   - Auto-assign Public IP: `ENABLED`

### Option B: Using CloudFormation (Advanced)

I'll create CloudFormation templates for you.

---

## 🌐 Step 4: Set Up Load Balancer (Optional but Recommended)

1. **Create Application Load Balancer**:
   - Go to EC2 → Load Balancers
   - Create Application Load Balancer
   - Name: `uav-service-alb`
   - Internet-facing
   - Port 80 (and 443 for HTTPS)

2. **Update ECS Service**:
   - Modify service to use load balancer
   - Target group port: 5000

---

## 🔐 Step 5: Configure Security

### Security Group Rules
- **Inbound**: 
  - Port 5000 from ALB Security Group
  - Port 80/443 from 0.0.0.0/0 (for ALB)
- **Outbound**: All traffic

### IAM Roles Required
- `ecsTaskExecutionRole`
- `ecsTaskRole` (if accessing other AWS services)

---

## 💾 Step 6: Database Setup (Important!)

Since you're using SQLite, you need persistent storage:

### Option 1: EFS (Elastic File System)
```bash
# Create EFS file system
aws efs create-file-system --tags Key=Name,Value=uav-service-efs
```

### Option 2: RDS (Recommended for Production)
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier uav-service-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123 \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx
```

---

## 📊 Step 7: Monitoring and Logging

### CloudWatch Setup
- Logs automatically sent to CloudWatch
- Set up alarms for CPU/Memory
- Create dashboard for monitoring

### Health Checks
- ALB health checks on `/health`
- ECS health checks configured

---

## 💰 Cost Estimation

### Monthly AWS Costs (us-east-1):
- **ECS Fargate**: ~$30-50/month (1 task, 1 vCPU, 2GB RAM)
- **Application Load Balancer**: ~$16/month
- **ECR Storage**: ~$1/month (for images)
- **CloudWatch Logs**: ~$1-5/month
- **RDS (if used)**: ~$15-25/month (db.t3.micro)

**Total: ~$63-97/month**

---

## 🚀 Quick Deployment Commands

Use these scripts for automated deployment:

### deploy-aws.sh (Linux/Mac)
```bash
#!/bin/bash
set -e

# Variables
REGION="us-east-1"
REPOSITORY_NAME="uav-service-management"
CLUSTER_NAME="uav-service-cluster"
SERVICE_NAME="uav-service"

echo "🚀 Starting AWS deployment..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $ACCOUNT_ID"

# Create ECR repository (if it doesn't exist)
aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $REGION || \
aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push
docker build -t $REPOSITORY_NAME .
docker tag $REPOSITORY_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest

echo "✅ Image pushed to ECR!"
echo "📦 Image URI: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest"
echo ""
echo "Next steps:"
echo "1. Go to ECS Console: https://console.aws.amazon.com/ecs/"
echo "2. Create cluster, task definition, and service"
echo "3. Use the image URI above"
```

### deploy-aws.bat (Windows)
```batch
@echo off
echo 🚀 Starting AWS deployment...

REM Get AWS account ID
for /f %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo Account ID: %ACCOUNT_ID%

REM Variables
set REGION=us-east-1
set REPOSITORY_NAME=uav-service-management

REM Create ECR repository
aws ecr describe-repositories --repository-names %REPOSITORY_NAME% --region %REGION% || aws ecr create-repository --repository-name %REPOSITORY_NAME% --region %REGION%

REM Login to ECR
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

REM Build and push
docker build -t %REPOSITORY_NAME% .
docker tag %REPOSITORY_NAME%:latest %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest
docker push %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest

echo ✅ Image pushed to ECR!
echo 📦 Image URI: %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPOSITORY_NAME%:latest
echo.
echo Next steps:
echo 1. Go to ECS Console: https://console.aws.amazon.com/ecs/
echo 2. Create cluster, task definition, and service
echo 3. Use the image URI above

pause
```

---

## 🔍 Troubleshooting

### Common Issues:
1. **ECR Permission Denied**: Check IAM permissions
2. **Task Won't Start**: Check CloudWatch logs
3. **Health Check Failing**: Verify port 5000 is exposed
4. **Database Connection**: Check security groups and networking

### Useful Commands:
```bash
# Check ECS tasks
aws ecs list-tasks --cluster uav-service-cluster

# Get task logs
aws logs get-log-events --log-group-name /ecs/uav-service-task

# Update service with new image
aws ecs update-service --cluster uav-service-cluster --service uav-service --force-new-deployment
```

---

## 🎯 Summary

Your deployment will provide:
- ✅ **Scalable container deployment** on AWS Fargate
- ✅ **Load balancing** with Application Load Balancer
- ✅ **Automatic scaling** based on demand
- ✅ **Monitoring and logging** with CloudWatch
- ✅ **Secure networking** with VPC and Security Groups
- ✅ **Persistent storage** options for database
- ✅ **Cost-effective** for small to medium applications

**Ready to deploy your UAV Service Management Tool to AWS! 🚁☁️**
