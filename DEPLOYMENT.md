# DUET Events Management System - Production Deployment Guide

## Prerequisites

### System Requirements
- Ubuntu 20.04+ or CentOS 8+
- Python 3.9+
- Nginx
- PostgreSQL 12+ (recommended) or SQLite (for small deployments)
- SSL certificate for HTTPS

### Installation Commands
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git -y

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Deployment Methods

### Method 1: Traditional Server Deployment

1. **Clone and setup application:**
```bash
cd /var/www
sudo git clone <your-repo-url> duet-events
cd duet-events
sudo ./deploy.sh
```

2. **Configure environment:**
```bash
sudo nano /var/www/duet-events/.env
```
Update the following variables:
- `SECRET_KEY`: Generate a strong secret key
- `DATABASE_URL`: Configure your database connection
- `MAIL_*`: Configure email settings
- `ADMIN_*`: Set admin credentials

3. **Configure SSL:**
```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

4. **Update nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/duet-events
# Update server_name with your domain
sudo nginx -t
sudo systemctl reload nginx
```

### Method 2: Docker Deployment

1. **Build and run with Docker Compose:**
```bash
# Clone repository
git clone <your-repo-url> duet-events
cd duet-events

# Copy environment file
cp .env.example .env
nano .env  # Edit with your settings

# Start services
docker-compose up -d
```

2. **Configure nginx for Docker:**
Update `docker-compose.yml` with your domain and SSL certificates.

## Database Setup

### PostgreSQL (Recommended for Production)
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE duet_events;
CREATE USER duet_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE duet_events TO duet_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://duet_user:secure_password@localhost/duet_events
```

### SQLite (Simple Setup)
```bash
# Already configured by default
DATABASE_URL=sqlite:///duet_events.db
```

## Security Configuration

### 1. Environment Variables
Ensure all sensitive data is in `.env` file:
```bash
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=your-database-url
ADMIN_PASSWORD=secure-admin-password
```

### 2. Firewall Configuration
```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. SSL/TLS Setup
```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 4. File Permissions
```bash
sudo chown -R www-data:www-data /var/www/duet-events
sudo chmod -R 755 /var/www/duet-events
sudo chmod -R 775 /var/www/duet-events/instance/uploads
```

## Monitoring and Maintenance

### 1. Service Management
```bash
# Check status
sudo systemctl status duet-events
sudo systemctl status nginx

# View logs
sudo journalctl -u duet-events -f
sudo tail -f /var/www/duet-events/logs/duet_events.log

# Restart services
sudo systemctl restart duet-events
sudo systemctl restart nginx
```

### 2. Backup Strategy
```bash
# Setup automated backups
sudo crontab -e
# Add line: 0 2 * * * /var/www/duet-events/backup.sh
```

### 3. Updates
```bash
cd /var/www/duet-events
sudo git pull origin main
sudo systemctl restart duet-events
```

## Performance Optimization

### 1. Gunicorn Configuration
Edit `duet-events.service` to adjust workers:
```ini
ExecStart=/var/www/duet-events/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 run:app
```

### 2. Database Optimization
```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

### 3. Nginx Caching
Add to nginx configuration:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Troubleshooting

### Common Issues

1. **Application won't start:**
```bash
sudo journalctl -u duet-events -f
# Check for Python errors or missing dependencies
```

2. **Database connection errors:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
# Test connection
sudo -u postgres psql -d duet_events
```

3. **Nginx configuration errors:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

4. **Permission errors:**
```bash
sudo chown -R www-data:www-data /var/www/duet-events
sudo chmod -R 755 /var/www/duet-events
```

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Service status
sudo systemctl is-active duet-events
sudo systemctl is-active nginx
```

## Scaling Considerations

### 1. Load Balancing
Use multiple application servers behind a load balancer.

### 2. Database Scaling
- Use connection pooling
- Consider read replicas for high traffic
- Implement database caching with Redis

### 3. File Storage
- Use cloud storage (AWS S3, etc.) for uploads
- Implement CDN for static assets

### 4. Monitoring
- Setup application monitoring (Sentry, etc.)
- Configure server monitoring (Prometheus, Grafana)
- Setup log aggregation

## Security Checklist

- [ ] Strong SECRET_KEY configured
- [ ] Database credentials secured
- [ ] SSL/TLS configured and working
- [ ] Firewall properly configured
- [ ] File permissions set correctly
- [ ] Regular backups scheduled
- [ ] Security headers configured in nginx
- [ ] Rate limiting enabled
- [ ] Admin password changed from default
- [ ] Environment variables secured (.env not in git)

## Contact and Support

For issues related to deployment or configuration, please:
1. Check the troubleshooting section
2. Review application logs
3. Contact the development team

Remember to regularly update your system and application dependencies for security!
