#!/bin/bash

# Security Hardening Script for DUET Events Management System

echo "Starting security hardening..."

# 1. Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Configure firewall
echo "Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 3. Configure fail2ban for SSH protection
echo "Installing and configuring fail2ban..."
sudo apt install fail2ban -y

sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# 4. Secure SSH configuration
echo "Securing SSH configuration..."
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

sudo tee -a /etc/ssh/sshd_config << EOF

# Security hardening
Protocol 2
PermitRootLogin no
PasswordAuthentication yes
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

sudo systemctl restart ssh

# 5. Install and configure automatic security updates
echo "Configuring automatic security updates..."
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades

# 6. Set up log monitoring
echo "Setting up log monitoring..."
sudo apt install logwatch -y

# 7. Install security tools
echo "Installing security monitoring tools..."
sudo apt install rkhunter chkrootkit -y

# 8. Configure file permissions for application
echo "Setting secure file permissions..."
APP_DIR="/var/www/duet-events"
if [ -d "$APP_DIR" ]; then
    sudo chown -R www-data:www-data $APP_DIR
    sudo chmod -R 750 $APP_DIR
    sudo chmod -R 755 $APP_DIR/app/static
    sudo chmod -R 775 $APP_DIR/instance/uploads
    sudo chmod -R 750 $APP_DIR/logs
    sudo chmod 600 $APP_DIR/.env
fi

# 9. Configure log rotation
echo "Configuring log rotation..."
sudo tee /etc/logrotate.d/duet-events << EOF
/var/www/duet-events/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload duet-events
    endscript
}
EOF

# 10. Create security monitoring script
echo "Creating security monitoring script..."
sudo tee /usr/local/bin/security-check.sh << 'EOF'
#!/bin/bash

echo "=== Security Check Report - $(date) ===" >> /var/log/security-check.log

echo "Checking for failed login attempts..." >> /var/log/security-check.log
lastb -n 10 >> /var/log/security-check.log

echo "Checking system users..." >> /var/log/security-check.log
awk -F: '$3 >= 1000 && $1 != "nobody" {print $1}' /etc/passwd >> /var/log/security-check.log

echo "Checking listening ports..." >> /var/log/security-check.log
netstat -tulpn | grep LISTEN >> /var/log/security-check.log

echo "=== End Report ===" >> /var/log/security-check.log
echo "" >> /var/log/security-check.log
EOF

sudo chmod +x /usr/local/bin/security-check.sh

# 11. Setup cron job for security monitoring
echo "Setting up security monitoring cron job..."
(crontab -l 2>/dev/null; echo "0 6 * * * /usr/local/bin/security-check.sh") | crontab -

# 12. Configure kernel parameters
echo "Configuring kernel security parameters..."
sudo tee -a /etc/sysctl.conf << EOF

# Security hardening
net.ipv4.conf.default.rp_filter=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.tcp_syncookies=1
net.ipv4.conf.all.accept_redirects=0
net.ipv6.conf.all.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.all.accept_source_route=0
net.ipv6.conf.all.accept_source_route=0
net.ipv4.conf.all.log_martians=1
EOF

sudo sysctl -p

echo "Security hardening completed!"
echo ""
echo "Security measures implemented:"
echo "✓ Firewall configured (UFW)"
echo "✓ Fail2ban installed and configured"
echo "✓ SSH hardened"
echo "✓ Automatic security updates enabled"
echo "✓ Log monitoring tools installed"
echo "✓ File permissions secured"
echo "✓ Log rotation configured"
echo "✓ Security monitoring script created"
echo "✓ Kernel security parameters configured"
echo ""
echo "Please review and test all configurations!"
echo "Consider setting up key-based SSH authentication and disabling password auth."
