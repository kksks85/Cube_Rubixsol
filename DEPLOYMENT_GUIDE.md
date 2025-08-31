# UAV Service Management Tool - Cloud Deployment Guide

## 🚀 Docker Deployment Guide

### Prerequisites
- Docker Desktop installed and running
- Git (for version control)
- 4GB+ RAM recommended
- 10GB+ free disk space

---

## 🏠 Local Development with Docker

### Quick Start
```bash
# Clone the repository (if needed)
git clone <your-repo-url>
cd CUBE

# Build and run with Docker Compose
docker-compose up --build

# Or use the deployment script
./deploy.sh          # Linux/Mac
deploy.bat           # Windows
```

### Access Your Application
- **Direct App Access**: http://localhost:5000
- **With Nginx Proxy**: http://localhost:80 (production profile)

### Docker Commands
```bash
# Build the image
docker build -t uav-service-management .

# Run container
docker run -p 5000:5000 uav-service-management

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker-compose down -v  # Remove volumes too
```

---

## ☁️ Cloud Deployment Options

### 1. AWS Deployment

#### AWS ECS (Elastic Container Service)
```bash
# Install AWS CLI
aws configure

# Build and push to ECR
aws ecr create-repository --repository-name uav-service-management
docker build -t uav-service-management .
docker tag uav-service-management:latest <account-id>.dkr.ecr.<region>.amazonaws.com/uav-service-management:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/uav-service-management:latest
```

#### AWS App Runner (Easiest)
1. Go to AWS App Runner console
2. Create service from container image
3. Use your ECR image URL
4. Configure auto-scaling and health checks

### 2. Google Cloud Platform

#### Google Cloud Run
```bash
# Install gcloud CLI
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/uav-service-management
gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/uav-service-management --platform managed
```

### 3. Microsoft Azure

#### Azure Container Instances
```bash
# Install Azure CLI
az login

# Create resource group
az group create --name uav-service-rg --location eastus

# Deploy container
az container create \
  --resource-group uav-service-rg \
  --name uav-service-app \
  --image uav-service-management:latest \
  --ports 5000 \
  --ip-address public
```

### 4. DigitalOcean App Platform
1. Connect your GitHub repository
2. Select Docker as build method
3. Configure environment variables
4. Deploy with auto-scaling

### 5. Heroku (Container Registry)
```bash
# Install Heroku CLI
heroku login
heroku container:login

# Create app and deploy
heroku create uav-service-management
heroku container:push web
heroku container:release web
```

---

## 🔧 Production Configuration

### Environment Variables
```bash
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/workorder.db  # or PostgreSQL URL
```

### SSL/HTTPS Setup
- Use cloud provider's load balancer (recommended)
- Or configure Nginx with SSL certificates
- Let's Encrypt for free certificates

### Database Considerations
- **Development**: SQLite (included)
- **Production**: PostgreSQL or MySQL
- **Cloud**: Use managed database services

### Scaling
- Use cloud auto-scaling groups
- Configure health checks
- Monitor resource usage

---

## 📊 Monitoring & Maintenance

### Health Checks
- Built-in health check at `/health`
- Container health checks configured
- Use cloud monitoring services

### Logs
```bash
# Container logs
docker-compose logs -f

# Cloud logs
# AWS CloudWatch, GCP Logging, Azure Monitor
```

### Backups
- Database: Regular snapshots
- Files: Persistent volume backups
- Use cloud backup services

---

## 🛡️ Security Best Practices

### Container Security
- Run as non-root user ✅ (already configured)
- Use minimal base image ✅
- Regular security updates
- Scan images for vulnerabilities

### Application Security
- Use HTTPS in production
- Configure CORS properly
- Set security headers ✅ (in nginx.conf)
- Regular dependency updates

---

## 💰 Cost Optimization

### Cloud Costs
- **AWS**: Use Spot instances for dev
- **GCP**: Use Cloud Run (pay per request)
- **Azure**: Use Container Instances
- Monitor usage and set billing alerts

### Resource Optimization
- Use multi-stage Docker builds
- Optimize image size
- Configure appropriate CPU/memory limits

---

## 🚀 Quick Cloud Deployment Commands

### AWS ECS
```bash
aws ecs create-cluster --cluster-name uav-service-cluster
# Follow AWS ECS deployment guide
```

### Google Cloud Run
```bash
gcloud run deploy uav-service --source . --platform managed --allow-unauthenticated
```

### Azure Container Instances
```bash
az container create --resource-group myResourceGroup --name uav-service --image uav-service-management:latest
```

---

## 📞 Support & Troubleshooting

### Common Issues
1. **Container won't start**: Check logs and environment variables
2. **Database issues**: Ensure volume persistence
3. **Port conflicts**: Use different ports
4. **Memory issues**: Increase container memory limits

### Getting Help
- Check Docker logs: `docker-compose logs`
- Verify health checks: `curl http://localhost:5000/health`
- Monitor resource usage: `docker stats`

---

**Your UAV Service Management Tool is ready for the cloud! 🚁☁️**
