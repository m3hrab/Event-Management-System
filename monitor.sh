#!/bin/bash

# DUET Events Monitoring Script
# This script monitors the health and performance of the application

LOG_FILE="/var/log/duet-events-monitor.log"
APP_URL="http://localhost:5000"
SERVICE_NAME="duet-events"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Function to send alert (customize with your notification method)
send_alert() {
    local message="$1"
    log_message "ALERT: $message"
    # Add your notification method here (email, Slack, etc.)
    # echo "$message" | mail -s "DUET Events Alert" admin@duet.ac.bd
}

# Check if service is running
check_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_message "Service $SERVICE_NAME is running"
        return 0
    else
        send_alert "Service $SERVICE_NAME is not running"
        return 1
    fi
}

# Check HTTP health endpoint
check_http_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health" --max-time 10)
    if [ "$response" = "200" ]; then
        log_message "HTTP health check passed"
        return 0
    else
        send_alert "HTTP health check failed with status: $response"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df /var/www/duet-events | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 80 ]; then
        send_alert "Disk usage is high: ${usage}%"
        return 1
    else
        log_message "Disk usage is normal: ${usage}%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$memory_usage" -gt 85 ]; then
        send_alert "Memory usage is high: ${memory_usage}%"
        return 1
    else
        log_message "Memory usage is normal: ${memory_usage}%"
        return 0
    fi
}

# Check log errors
check_log_errors() {
    local error_count=$(journalctl -u $SERVICE_NAME --since "5 minutes ago" | grep -i error | wc -l)
    if [ "$error_count" -gt 10 ]; then
        send_alert "High number of errors in logs: $error_count errors in last 5 minutes"
        return 1
    else
        log_message "Log error count is normal: $error_count errors in last 5 minutes"
        return 0
    fi
}

# Check database connectivity
check_database() {
    local db_check=$(cd /var/www/duet-events && sudo -u www-data ./venv/bin/python -c "
from app import create_app, db
try:
    app = create_app('production')
    with app.app_context():
        db.session.execute('SELECT 1')
    print('OK')
except Exception as e:
    print('ERROR')
" 2>/dev/null)
    
    if [ "$db_check" = "OK" ]; then
        log_message "Database connectivity check passed"
        return 0
    else
        send_alert "Database connectivity check failed"
        return 1
    fi
}

# Main monitoring function
main() {
    log_message "Starting monitoring check"
    
    local checks_passed=0
    local total_checks=6
    
    # Run all checks
    check_service && ((checks_passed++))
    check_http_health && ((checks_passed++))
    check_disk_space && ((checks_passed++))
    check_memory && ((checks_passed++))
    check_log_errors && ((checks_passed++))
    check_database && ((checks_passed++))
    
    # Summary
    log_message "Monitoring check completed: $checks_passed/$total_checks checks passed"
    
    if [ "$checks_passed" -lt "$total_checks" ]; then
        send_alert "Some health checks failed: $checks_passed/$total_checks passed"
        exit 1
    else
        log_message "All health checks passed"
        exit 0
    fi
}

# Create log file if it doesn't exist
touch $LOG_FILE

# Run monitoring
main
