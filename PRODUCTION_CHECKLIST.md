# Production Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] Server with Ubuntu 20.04+ or CentOS 8+
- [ ] Python 3.9+ installed
- [ ] Nginx installed and configured
- [ ] PostgreSQL installed (recommended) or SQLite for small deployments
- [ ] SSL certificate obtained
- [ ] Domain name configured
- [ ] Firewall configured

### Application Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` changed to a strong, unique value
- [ ] `DATABASE_URL` configured for production database
- [ ] `FLASK_ENV` set to `production`
- [ ] `FLASK_DEBUG` set to `False`
- [ ] Admin credentials configured
- [ ] Email settings configured (if using email features)

### Security
- [ ] Strong passwords for all accounts
- [ ] Database credentials secured
- [ ] File permissions set correctly
- [ ] SSH key-based authentication configured
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates installed
- [ ] Security headers configured in nginx

## Deployment

### Code Deployment
- [ ] Code pushed to production repository
- [ ] Virtual environment created
- [ ] Dependencies installed from `requirements.txt`
- [ ] Database migrations run
- [ ] Static files configured
- [ ] Upload directories created with correct permissions

### Service Configuration
- [ ] Systemd service file installed
- [ ] Service enabled and started
- [ ] Nginx configuration installed
- [ ] Nginx reloaded
- [ ] SSL configuration tested

### Testing
- [ ] Application starts without errors
- [ ] Health check endpoint responds correctly
- [ ] Database connectivity verified
- [ ] File upload functionality tested
- [ ] SSL certificate working
- [ ] All major features tested

## Post-Deployment

### Monitoring Setup
- [ ] Log rotation configured
- [ ] Monitoring script scheduled
- [ ] Error tracking configured (optional: Sentry)
- [ ] Backup script scheduled
- [ ] Health checks configured

### Security Hardening
- [ ] Security hardening script run
- [ ] Fail2ban configured
- [ ] Log monitoring enabled
- [ ] Automatic security updates enabled
- [ ] Regular security scans scheduled

### Performance Optimization
- [ ] Gunicorn worker count optimized
- [ ] Nginx caching configured
- [ ] Database performance tuned
- [ ] Static file serving optimized

### Documentation
- [ ] Deployment documentation updated
- [ ] Admin access credentials documented securely
- [ ] Backup and recovery procedures documented
- [ ] Monitoring and alerting procedures documented

## Maintenance

### Regular Tasks
- [ ] Weekly: Review logs for errors
- [ ] Weekly: Check disk space and performance
- [ ] Monthly: Update system packages
- [ ] Monthly: Review and rotate credentials
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

### Emergency Procedures
- [ ] Incident response plan documented
- [ ] Backup restoration procedure tested
- [ ] Rollback procedure documented
- [ ] Emergency contact list updated

## Monitoring Endpoints

- Application health: `https://your-domain.com/health`
- Service status: `sudo systemctl status duet-events`
- Logs: `sudo journalctl -u duet-events -f`
- Nginx status: `sudo systemctl status nginx`

## Important Commands

```bash
# Start/stop application
sudo systemctl start duet-events
sudo systemctl stop duet-events
sudo systemctl restart duet-events

# View logs
sudo journalctl -u duet-events -f
sudo tail -f /var/www/duet-events/logs/duet_events.log

# Backup
sudo /var/www/duet-events/backup.sh

# Monitoring
sudo /var/www/duet-events/monitor.sh

# Security check
sudo /var/www/duet-events/security-setup.sh
```

## Troubleshooting

### Common Issues
1. **Service won't start**: Check logs and configuration
2. **Database errors**: Verify connection string and credentials
3. **Permission errors**: Check file ownership and permissions
4. **SSL issues**: Verify certificate installation and nginx config
5. **High resource usage**: Check application logs and system metrics

### Emergency Contacts
- System Administrator: [Your contact info]
- Application Developer: [Your contact info]
- Domain/SSL Provider: [Provider contact info]
- Hosting Provider: [Provider contact info]

---

**Note**: Always test deployments in a staging environment before production deployment.
