# CUBE PRO Docker Deployment Guide

## 🐳 Docker Images Created

### Available Images
- `cube-pro:latest` - Latest development version
- `cube-pro:v1.2` - Current stable version  
- `cube-pro:production` - Production ready version

### Image Details
- **Base Image**: Python 3.11-slim
- **Size**: ~830MB
- **Architecture**: Multi-platform (Linux/amd64)
- **User**: Non-root user (appuser)
- **Health Check**: Built-in HTTP health check

## 🚀 Quick Start

### Option 1: Using Docker Run (Simple)
```bash
# Run the application
docker run -d \
  --name cube-pro \
  -p 5000:5000 \
  -v cube-data:/app/instance \
  -v cube-uploads:/app/app/static/uploads \
  cube-pro:latest

# Check status
docker ps
docker logs cube-pro

# Access the application
# Open browser to: http://localhost:5000
```

### Option 2: Using Docker Compose (Recommended)
```bash
# Start the application
docker-compose up -d

# Start with nginx proxy (production)
docker-compose --profile production up -d

# Check status
docker-compose ps
docker-compose logs cube-pro-app

# Stop the application
docker-compose down
```

## 📋 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_APP` | `run.py` | Flask application entry point |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

## 💾 Data Persistence

### Volumes
- **Database**: `/app/instance` - SQLite database and configuration
- **Uploads**: `/app/app/static/uploads` - User uploaded files

### Backup Data
```bash
# Backup database
docker cp cube-pro:/app/instance/workorder.db ./backup/

# Backup uploads
docker cp cube-pro:/app/app/static/uploads ./backup/
```

## 🔧 Configuration

### Custom Configuration
Create a `.env` file in your project directory:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/workorder.db
```

Mount it in the container:
```bash
docker run -d \
  --name cube-pro \
  -p 5000:5000 \
  --env-file .env \
  -v cube-data:/app/instance \
  cube-pro:latest
```

## 🌐 Production Deployment

### With Nginx Reverse Proxy
```bash
# Start with production profile
docker-compose --profile production up -d

# This starts:
# - cube-pro-app on internal network
# - nginx proxy on ports 80/443
```

### SSL Configuration
1. Place SSL certificates in `./ssl/` directory
2. Update `nginx.conf` with your domain
3. Start with production profile

## 🔍 Monitoring & Logs

### Check Application Health
```bash
# Container health
docker ps

# Application logs
docker logs cube-pro-app

# Follow logs
docker logs -f cube-pro-app

# Health check
curl http://localhost:5000/
```

### Troubleshooting
```bash
# Check container status
docker inspect cube-pro-app

# Access container shell
docker exec -it cube-pro-app bash

# Check database
docker exec -it cube-pro-app python check_db.py
```

## 📦 Building Custom Images

### Build from Source
```bash
# Clone repository
git clone https://github.com/kksks85/Cube_Rubixsol.git
cd Cube_Rubixsol

# Build image
docker build -t cube-pro:custom .

# Run custom image
docker run -d --name cube-pro-custom -p 5000:5000 cube-pro:custom
```

### Multi-stage Build (Production)
```bash
# Build production image
docker build -f Dockerfile.production -t cube-pro:prod .
```

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin master

# Rebuild image
docker-compose build

# Restart with new image
docker-compose up -d
```

### Database Maintenance
```bash
# Backup before updates
docker exec cube-pro-app python -c "
import sqlite3
import shutil
shutil.copy('/app/instance/workorder.db', '/app/instance/workorder_backup.db')
print('Database backed up successfully')
"
```

## 🛡️ Security Best Practices

1. **Use non-root user** ✅ (Built-in)
2. **Regular updates**: Update base images regularly
3. **Secrets management**: Use Docker secrets or external vault
4. **Network isolation**: Use custom networks
5. **Resource limits**: Set memory/CPU limits

### Resource Limits Example
```yaml
services:
  cube-pro-app:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## 📈 Scaling

### Multiple Instances
```bash
# Scale to 3 instances
docker-compose up -d --scale cube-pro-app=3

# Load balance with nginx
# Update nginx.conf with upstream configuration
```

## 🆘 Support

### Common Issues
1. **Port conflicts**: Change port mapping `-p 8080:5000`
2. **Permission issues**: Check volume permissions
3. **Database issues**: Check `/app/instance` volume mount
4. **Memory issues**: Increase Docker memory allocation

### Get Help
- Check logs: `docker logs cube-pro-app`
- Access shell: `docker exec -it cube-pro-app bash`
- Health check: `curl http://localhost:5000/`

---

**✅ Docker image successfully created and tested!**
**🌐 Application accessible at: http://localhost:5000**
