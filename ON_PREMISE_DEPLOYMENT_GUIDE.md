# CUBE On-Premise Deployment and Release Management Guide

## Table of Contents
1. [On-Premise Server Implementation](#on-premise-server-implementation)
2. [Environment Setup](#environment-setup)
3. [Database Management](#database-management)
4. [Development and Production Release Strategy](#development-and-production-release-strategy)
5. [Data Protection and Backup Strategy](#data-protection-and-backup-strategy)
6. [Zero-Downtime Deployment](#zero-downtime-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## On-Premise Server Implementation

### System Requirements

#### Minimum Hardware Requirements
- **CPU**: 4 cores (Intel Xeon or AMD EPYC recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 500GB SSD (for OS, application, and database)
- **Network**: Gigabit Ethernet connection
- **Backup Storage**: Additional 1TB for backups

#### Recommended Production Hardware
- **CPU**: 8+ cores
- **RAM**: 32GB or higher
- **Storage**: 1TB+ NVMe SSD
- **Network**: Redundant Gigabit connections
- **Backup**: Network-attached storage (NAS) or dedicated backup server

### Operating System Setup

#### Ubuntu Server 22.04 LTS (Recommended)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git curl wget htop

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### CentOS/RHEL 8/9 Alternative
```bash
# Update system
sudo dnf update -y

# Install EPEL repository
sudo dnf install -y epel-release

# Install essential packages
sudo dnf install -y python3 python3-pip nginx postgresql postgresql-server redis git
```

---

## Environment Setup

### 1. Create Dedicated User
```bash
# Create application user
sudo useradd -m -s /bin/bash cubeapp
sudo usermod -aG sudo cubeapp

# Switch to application user
sudo su - cubeapp
```

### 2. Directory Structure
```bash
# Create application directories
mkdir -p /home/cubeapp/{
    cube-prod,
    cube-dev,
    cube-staging,
    backups,
    logs,
    scripts
}
```

### 3. Database Setup

#### PostgreSQL Configuration
```bash
# Initialize PostgreSQL (CentOS/RHEL only)
sudo postgresql-setup --initdb

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create databases
sudo -u postgres psql << EOF
CREATE DATABASE cube_prod;
CREATE DATABASE cube_dev;
CREATE DATABASE cube_staging;
CREATE USER cubeapp WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE cube_prod TO cubeapp;
GRANT ALL PRIVILEGES ON DATABASE cube_dev TO cubeapp;
GRANT ALL PRIVILEGES ON DATABASE cube_staging TO cubeapp;
\q
EOF
```

### 4. Application Deployment

#### Production Environment
```bash
cd /home/cubeapp/cube-prod

# Clone repository
git clone https://github.com/kksks85/Cube_Rubixsol.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production configuration
cp .env.example .env.prod
```

#### Development Environment
```bash
cd /home/cubeapp/cube-dev

# Clone repository
git clone https://github.com/kksks85/Cube_Rubixsol.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create development configuration
cp .env.example .env.dev
```

---

## Database Management

### 1. Environment-Specific Configuration

#### Production Database Config (.env.prod)
```bash
# Database Configuration
DATABASE_URL=postgresql://cubeapp:your_secure_password@localhost/cube_prod
SQLALCHEMY_DATABASE_URI=postgresql://cubeapp:your_secure_password@localhost/cube_prod

# Flask Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your_production_secret_key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Settings
CUBE_ENV=production
LOG_LEVEL=INFO
```

#### Development Database Config (.env.dev)
```bash
# Database Configuration
DATABASE_URL=postgresql://cubeapp:your_secure_password@localhost/cube_dev
SQLALCHEMY_DATABASE_URI=postgresql://cubeapp:your_secure_password@localhost/cube_dev

# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your_development_secret_key

# Redis Configuration
REDIS_URL=redis://localhost:6379/1

# Application Settings
CUBE_ENV=development
LOG_LEVEL=DEBUG
```

### 2. Database Migration Strategy

#### Create Migration Scripts
```bash
# Create migration script directory
mkdir -p /home/cubeapp/scripts/migrations

# Database backup script
cat > /home/cubeapp/scripts/db_backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/cubeapp/backups"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup production database
pg_dump -h localhost -U cubeapp cube_prod > $BACKUP_DIR/cube_prod_$TIMESTAMP.sql

# Backup development database
pg_dump -h localhost -U cubeapp cube_dev > $BACKUP_DIR/cube_dev_$TIMESTAMP.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

echo "Database backup completed: $TIMESTAMP"
EOF

chmod +x /home/cubeapp/scripts/db_backup.sh
```

#### Database Migration Script
```bash
cat > /home/cubeapp/scripts/migrate_database.sh << 'EOF'
#!/bin/bash
ENVIRONMENT=$1
if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 [prod|dev|staging]"
    exit 1
fi

CUBE_DIR="/home/cubeapp/cube-$ENVIRONMENT"
cd $CUBE_DIR

# Activate virtual environment
source venv/bin/activate

# Load environment variables
source .env.$ENVIRONMENT

# Create backup before migration
/home/cubeapp/scripts/db_backup.sh

# Run migrations
echo "Running database migrations for $ENVIRONMENT..."
flask db upgrade

if [ $? -eq 0 ]; then
    echo "Migration completed successfully for $ENVIRONMENT"
else
    echo "Migration failed for $ENVIRONMENT"
    exit 1
fi
EOF

chmod +x /home/cubeapp/scripts/migrate_database.sh
```

---

## Development and Production Release Strategy

### 1. Git Workflow Strategy

#### Branch Structure
```
master (production-ready)
├── develop (integration branch)
├── feature/feature-name (feature development)
├── release/version-number (release preparation)
└── hotfix/issue-description (emergency fixes)
```

#### Release Process
```bash
# Create release script
cat > /home/cubeapp/scripts/deploy_release.sh << 'EOF'
#!/bin/bash
ENVIRONMENT=$1
VERSION=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 [prod|staging] [version]"
    exit 1
fi

CUBE_DIR="/home/cubeapp/cube-$ENVIRONMENT"
BACKUP_DIR="/home/cubeapp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting deployment to $ENVIRONMENT - Version $VERSION"

# 1. Create application backup
echo "Creating application backup..."
tar -czf $BACKUP_DIR/cube_${ENVIRONMENT}_${TIMESTAMP}.tar.gz -C /home/cubeapp cube-$ENVIRONMENT

# 2. Create database backup
echo "Creating database backup..."
/home/cubeapp/scripts/db_backup.sh

# 3. Navigate to application directory
cd $CUBE_DIR

# 4. Put application in maintenance mode (for production)
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "Enabling maintenance mode..."
    touch maintenance.flag
    sudo systemctl reload nginx
fi

# 5. Pull latest code
echo "Pulling latest code..."
git fetch origin
git checkout $VERSION

# 6. Update dependencies
echo "Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 7. Run database migrations
echo "Running database migrations..."
/home/cubeapp/scripts/migrate_database.sh $ENVIRONMENT

# 8. Collect static files (if applicable)
echo "Collecting static files..."
# Add static file collection if needed

# 9. Restart application services
echo "Restarting application services..."
sudo systemctl restart cube-$ENVIRONMENT
sudo systemctl restart nginx

# 10. Remove maintenance mode (for production)
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "Disabling maintenance mode..."
    rm -f maintenance.flag
    sudo systemctl reload nginx
fi

# 11. Verify deployment
echo "Verifying deployment..."
sleep 5
curl -f http://localhost:8000/health || echo "Warning: Health check failed"

echo "Deployment completed successfully!"
EOF

chmod +x /home/cubeapp/scripts/deploy_release.sh
```

### 2. Staging Environment Setup

#### Create Staging Configuration
```bash
# Staging database
sudo -u postgres psql << EOF
CREATE DATABASE cube_staging;
GRANT ALL PRIVILEGES ON DATABASE cube_staging TO cubeapp;
\q
EOF

# Staging environment config
cd /home/cubeapp/cube-staging
cp .env.example .env.staging

# Configure staging settings
cat > .env.staging << 'EOF'
DATABASE_URL=postgresql://cubeapp:your_secure_password@localhost/cube_staging
SQLALCHEMY_DATABASE_URI=postgresql://cubeapp:your_secure_password@localhost/cube_staging
FLASK_ENV=staging
DEBUG=False
SECRET_KEY=your_staging_secret_key
REDIS_URL=redis://localhost:6379/2
CUBE_ENV=staging
LOG_LEVEL=INFO
EOF
```

---

## Data Protection and Backup Strategy

### 1. Automated Backup System

#### Daily Backup Cron Job
```bash
# Add to crontab
crontab -e

# Add these lines:
# Daily database backup at 2 AM
0 2 * * * /home/cubeapp/scripts/db_backup.sh

# Weekly full application backup at 3 AM on Sundays
0 3 * * 0 /home/cubeapp/scripts/full_backup.sh

# Clean old backups daily at 4 AM
0 4 * * * find /home/cubeapp/backups -name "*.sql" -mtime +30 -delete
```

#### Full Application Backup Script
```bash
cat > /home/cubeapp/scripts/full_backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/cubeapp/backups"

# Create weekly backup directory
mkdir -p $BACKUP_DIR/weekly

# Backup all application directories
tar -czf $BACKUP_DIR/weekly/cube_full_$TIMESTAMP.tar.gz \
    -C /home/cubeapp \
    cube-prod cube-dev cube-staging scripts

# Backup databases
pg_dump -h localhost -U cubeapp cube_prod > $BACKUP_DIR/weekly/cube_prod_$TIMESTAMP.sql
pg_dump -h localhost -U cubeapp cube_dev > $BACKUP_DIR/weekly/cube_dev_$TIMESTAMP.sql
pg_dump -h localhost -U cubeapp cube_staging > $BACKUP_DIR/weekly/cube_staging_$TIMESTAMP.sql

# Keep only last 12 weeks of backups
find $BACKUP_DIR/weekly -name "*" -mtime +84 -delete

echo "Full backup completed: $TIMESTAMP"
EOF

chmod +x /home/cubeapp/scripts/full_backup.sh
```

### 2. Disaster Recovery Plan

#### Database Recovery Script
```bash
cat > /home/cubeapp/scripts/restore_database.sh << 'EOF'
#!/bin/bash
ENVIRONMENT=$1
BACKUP_FILE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 [prod|dev|staging] [backup_file.sql]"
    exit 1
fi

echo "WARNING: This will restore database for $ENVIRONMENT environment"
echo "All current data will be lost!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled"
    exit 1
fi

# Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS cube_$ENVIRONMENT;
CREATE DATABASE cube_$ENVIRONMENT;
GRANT ALL PRIVILEGES ON DATABASE cube_$ENVIRONMENT TO cubeapp;
\q
EOF

# Restore from backup
psql -h localhost -U cubeapp cube_$ENVIRONMENT < $BACKUP_FILE

echo "Database restored successfully from $BACKUP_FILE"
EOF

chmod +x /home/cubeapp/scripts/restore_database.sh
```

---

## Zero-Downtime Deployment

### 1. Load Balancer Setup with Nginx

#### Nginx Configuration
```bash
sudo cat > /etc/nginx/sites-available/cube << 'EOF'
upstream cube_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002 backup;
}

server {
    listen 80;
    server_name your-domain.com;

    # Maintenance mode
    if (-f /home/cubeapp/cube-prod/maintenance.flag) {
        return 503;
    }

    # Static files
    location /static {
        alias /home/cubeapp/cube-prod/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://cube_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://cube_backend;
        access_log off;
    }

    # Maintenance page
    error_page 503 @maintenance;
    location @maintenance {
        root /home/cubeapp/maintenance;
        rewrite ^(.*)$ /maintenance.html break;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/cube /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Blue-Green Deployment Script

```bash
cat > /home/cubeapp/scripts/blue_green_deploy.sh << 'EOF'
#!/bin/bash
VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 [version]"
    exit 1
fi

BLUE_DIR="/home/cubeapp/cube-prod"
GREEN_DIR="/home/cubeapp/cube-green"
BACKUP_DIR="/home/cubeapp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting Blue-Green deployment - Version $VERSION"

# 1. Prepare green environment
echo "Preparing green environment..."
if [ -d "$GREEN_DIR" ]; then
    rm -rf $GREEN_DIR
fi

cp -r $BLUE_DIR $GREEN_DIR
cd $GREEN_DIR

# 2. Update green environment
echo "Updating green environment..."
git fetch origin
git checkout $VERSION
source venv/bin/activate
pip install -r requirements.txt

# 3. Test green environment
echo "Testing green environment..."
export FLASK_APP=run.py
export FLASK_ENV=production
flask db upgrade
python -c "import app; print('Green environment test passed')"

# 4. Start green application on port 8002
echo "Starting green application..."
gunicorn -w 4 -b 127.0.0.1:8002 run:app --daemon

# 5. Health check
echo "Performing health check..."
sleep 10
curl -f http://127.0.0.1:8002/health || {
    echo "Health check failed, rolling back..."
    pkill -f "gunicorn.*8002"
    exit 1
}

# 6. Switch traffic to green
echo "Switching traffic to green environment..."
sudo sed -i 's/server 127.0.0.1:8001;/server 127.0.0.1:8002;/' /etc/nginx/sites-available/cube
sudo sed -i 's/server 127.0.0.1:8002 backup;/server 127.0.0.1:8001 backup;/' /etc/nginx/sites-available/cube
sudo nginx -t && sudo systemctl reload nginx

# 7. Stop blue application
echo "Stopping blue application..."
pkill -f "gunicorn.*8001"

# 8. Swap directories
echo "Swapping environments..."
mv $BLUE_DIR ${BLUE_DIR}_old
mv $GREEN_DIR $BLUE_DIR

# 9. Start new blue application on port 8001
echo "Starting new blue application..."
cd $BLUE_DIR
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8001 run:app --daemon

# 10. Final health check
echo "Final health check..."
sleep 5
curl -f http://127.0.0.1:8001/health || echo "Warning: Final health check failed"

# 11. Cleanup
echo "Cleaning up..."
rm -rf ${BLUE_DIR}_old

echo "Blue-Green deployment completed successfully!"
EOF

chmod +x /home/cubeapp/scripts/blue_green_deploy.sh
```

---

## Monitoring and Maintenance

### 1. System Monitoring

#### Create Monitoring Script
```bash
cat > /home/cubeapp/scripts/system_monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/home/cubeapp/logs/system_monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# System metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

# Application health
APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
DB_STATUS=$(pg_isready -h localhost -U cubeapp && echo "OK" || echo "FAIL")

# Log metrics
echo "[$TIMESTAMP] CPU: ${CPU_USAGE}%, Memory: ${MEMORY_USAGE}%, Disk: ${DISK_USAGE}%, App: $APP_STATUS, DB: $DB_STATUS" >> $LOG_FILE

# Alert if thresholds exceeded
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "[$TIMESTAMP] ALERT: High CPU usage: ${CPU_USAGE}%" >> $LOG_FILE
fi

if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "[$TIMESTAMP] ALERT: High memory usage: ${MEMORY_USAGE}%" >> $LOG_FILE
fi

if [ "$APP_STATUS" != "200" ]; then
    echo "[$TIMESTAMP] ALERT: Application health check failed: $APP_STATUS" >> $LOG_FILE
fi
EOF

chmod +x /home/cubeapp/scripts/system_monitor.sh

# Add to crontab for every 5 minutes
crontab -e
# Add: */5 * * * * /home/cubeapp/scripts/system_monitor.sh
```

### 2. Log Rotation

```bash
sudo cat > /etc/logrotate.d/cube << 'EOF'
/home/cubeapp/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 cubeapp cubeapp
    postrotate
        systemctl reload cube-prod
    endscript
}
EOF
```

---

## Security Best Practices

### 1. Server Hardening

#### Firewall Configuration
```bash
# Install and configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### SSL/TLS Setup with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Application Security

#### Environment Variable Security
```bash
# Secure environment files
chmod 600 /home/cubeapp/cube-*/.env*
chown cubeapp:cubeapp /home/cubeapp/cube-*/.env*
```

#### Database Security
```bash
# PostgreSQL security configuration
sudo -u postgres psql << 'EOF'
-- Create read-only user for monitoring
CREATE USER cube_monitor WITH PASSWORD 'monitor_password';
GRANT CONNECT ON DATABASE cube_prod TO cube_monitor;
GRANT USAGE ON SCHEMA public TO cube_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cube_monitor;

-- Set password policies
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();
EOF
```

---

## Troubleshooting

### 1. Common Issues and Solutions

#### Application Won't Start
```bash
# Check logs
tail -f /home/cubeapp/logs/cube.log

# Check process status
ps aux | grep gunicorn

# Check database connectivity
pg_isready -h localhost -U cubeapp

# Restart services
sudo systemctl restart cube-prod
sudo systemctl restart nginx
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Reset connections
sudo systemctl restart postgresql
```

#### Performance Issues
```bash
# Monitor system resources
htop

# Check database performance
sudo -u postgres psql cube_prod -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Analyze slow queries
sudo -u postgres psql cube_prod -c "SELECT query, mean_time, calls FROM pg_stat_statements WHERE mean_time > 1000 ORDER BY mean_time DESC;"
```

### 2. Rollback Procedures

#### Emergency Rollback Script
```bash
cat > /home/cubeapp/scripts/emergency_rollback.sh << 'EOF'
#!/bin/bash
BACKUP_TIMESTAMP=$1

if [ -z "$BACKUP_TIMESTAMP" ]; then
    echo "Usage: $0 [backup_timestamp]"
    echo "Available backups:"
    ls -la /home/cubeapp/backups/cube_prod_*.tar.gz
    exit 1
fi

echo "EMERGENCY ROLLBACK INITIATED"
echo "Rolling back to backup: $BACKUP_TIMESTAMP"

# Stop current application
sudo systemctl stop cube-prod

# Restore application
cd /home/cubeapp
tar -xzf backups/cube_prod_${BACKUP_TIMESTAMP}.tar.gz

# Restore database
/home/cubeapp/scripts/restore_database.sh prod backups/cube_prod_${BACKUP_TIMESTAMP}.sql

# Start application
sudo systemctl start cube-prod
sudo systemctl reload nginx

echo "Emergency rollback completed!"
EOF

chmod +x /home/cubeapp/scripts/emergency_rollback.sh
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] Database migrations tested in staging
- [ ] Backup created
- [ ] Dependencies updated
- [ ] Security scan completed
- [ ] Performance testing passed

### During Deployment
- [ ] Maintenance mode enabled (if required)
- [ ] Application stopped gracefully
- [ ] Code updated
- [ ] Database migrated
- [ ] Dependencies installed
- [ ] Configuration updated
- [ ] Application started
- [ ] Health check passed

### Post-Deployment
- [ ] Maintenance mode disabled
- [ ] Functionality tested
- [ ] Performance metrics verified
- [ ] Error logs checked
- [ ] Backup verified
- [ ] Documentation updated

---

## Support and Maintenance

### Regular Maintenance Tasks

#### Weekly
- Review system logs
- Check backup integrity
- Update dependencies
- Performance review

#### Monthly
- Security updates
- Database maintenance
- Capacity planning
- Disaster recovery testing

#### Quarterly
- Full system audit
- Security assessment
- Performance optimization
- Documentation updates

---

This comprehensive guide provides a robust foundation for implementing CUBE on an on-premise server with proper development and production release management, ensuring minimal data loss and productivity disruption.
