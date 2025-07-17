#!/bin/bash

# Production Verification Script
# Run this script after deployment to verify everything is working correctly

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

APP_DIR="/var/www/duet-events"
SERVICE_NAME="duet-events"
DOMAIN="localhost"  # Change to your domain

echo -e "${YELLOW}Starting production verification...${NC}"
echo ""

# Function to check and report status
check_status() {
    local check_name="$1"
    local status="$2"
    
    if [ "$status" -eq 0 ]; then
        echo -e "✅ ${GREEN}$check_name: PASS${NC}"
        return 0
    else
        echo -e "❌ ${RED}$check_name: FAIL${NC}"
        return 1
    fi
}

# Check 1: Service is running
echo "Checking service status..."
systemctl is-active --quiet $SERVICE_NAME
check_status "Service $SERVICE_NAME running" $?

# Check 2: Nginx is running
echo "Checking nginx status..."
systemctl is-active --quiet nginx
check_status "Nginx service running" $?

# Check 3: Application responds to HTTP
echo "Checking HTTP response..."
response=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" --max-time 10)
if [ "$response" = "200" ]; then
    check_status "HTTP response (200)" 0
else
    check_status "HTTP response ($response)" 1
fi

# Check 4: Health endpoint
echo "Checking health endpoint..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/health" --max-time 10)
if [ "$health_response" = "200" ]; then
    check_status "Health endpoint (/health)" 0
else
    check_status "Health endpoint ($health_response)" 1
fi

# Check 5: Database connectivity
echo "Checking database connectivity..."
if [ -d "$APP_DIR" ]; then
    db_check=$(cd $APP_DIR && sudo -u www-data ./venv/bin/python -c "
from app import create_app, db
try:
    app = create_app('production')
    with app.app_context():
        db.session.execute('SELECT 1')
    print('OK')
except Exception as e:
    print('ERROR:', str(e))
" 2>/dev/null)
    
    if [[ "$db_check" == *"OK"* ]]; then
        check_status "Database connectivity" 0
    else
        check_status "Database connectivity" 1
        echo "  Error: $db_check"
    fi
else
    check_status "Application directory exists" 1
fi

# Check 6: File permissions
echo "Checking file permissions..."
if [ -d "$APP_DIR" ]; then
    owner=$(stat -c '%U:%G' $APP_DIR)
    if [ "$owner" = "www-data:www-data" ]; then
        check_status "File ownership (www-data:www-data)" 0
    else
        check_status "File ownership ($owner)" 1
    fi
else
    check_status "Application directory permissions" 1
fi

# Check 7: Log files
echo "Checking log files..."
if [ -f "$APP_DIR/logs/duet_events.log" ]; then
    check_status "Application log file exists" 0
else
    check_status "Application log file exists" 1
fi

# Check 8: Upload directory
echo "Checking upload directory..."
if [ -d "$APP_DIR/instance/uploads" ]; then
    upload_perms=$(stat -c '%a' "$APP_DIR/instance/uploads")
    if [ "$upload_perms" = "775" ]; then
        check_status "Upload directory permissions (775)" 0
    else
        check_status "Upload directory permissions ($upload_perms)" 1
    fi
else
    check_status "Upload directory exists" 1
fi

# Check 9: Environment file
echo "Checking environment configuration..."
if [ -f "$APP_DIR/.env" ]; then
    env_perms=$(stat -c '%a' "$APP_DIR/.env")
    if [ "$env_perms" = "600" ]; then
        check_status "Environment file permissions (600)" 0
    else
        check_status "Environment file permissions ($env_perms)" 1
    fi
else
    check_status "Environment file exists" 1
fi

# Check 10: SSL certificate (if HTTPS is configured)
echo "Checking SSL configuration..."
if command -v openssl >/dev/null 2>&1; then
    ssl_check=$(echo | timeout 5 openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | grep "Verify return code")
    if [[ "$ssl_check" == *"0 (ok)"* ]]; then
        check_status "SSL certificate valid" 0
    else
        check_status "SSL certificate (optional)" 1
        echo "  Note: SSL may not be configured or domain may be localhost"
    fi
else
    check_status "SSL check (openssl not available)" 1
fi

echo ""
echo -e "${YELLOW}Verification completed!${NC}"
echo ""

# Summary
echo "=== SUMMARY ==="
echo "Service Status:"
systemctl status $SERVICE_NAME --no-pager -l | head -3
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager -l | head -3
echo ""

echo "Recent application logs:"
if [ -f "$APP_DIR/logs/duet_events.log" ]; then
    tail -5 "$APP_DIR/logs/duet_events.log"
else
    echo "No application logs found"
fi

echo ""
echo "=== NEXT STEPS ==="
echo "1. Test the application in a web browser"
echo "2. Create test user accounts and verify functionality"
echo "3. Configure SSL/TLS if not already done"
echo "4. Set up monitoring and alerting"
echo "5. Schedule regular backups"
echo ""
echo "Application URL: http://$DOMAIN"
echo "Health Check: http://$DOMAIN/health"
echo "Admin Login: admin@duet.ac.bd / admin123 (CHANGE THIS!)"
