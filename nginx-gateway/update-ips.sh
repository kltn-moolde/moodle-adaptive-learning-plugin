#!/bin/bash

# Script to update IP addresses in NGINX configuration
# This script helps you easily update backend service IPs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NGINX_DIR="/opt/nginx-gateway"
CONFIG_FILE="${SCRIPT_DIR}/config.env"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "NGINX Gateway IP Configuration Script"
    echo "====================================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  show        Show current IP configuration"
    echo "  update      Update IPs interactively"
    echo "  auto        Auto-detect and update IPs"
    echo "  set         Set specific service IP"
    echo "  apply       Apply configuration changes"
    echo "  help        Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 show"
    echo "  $0 update"
    echo "  $0 set user-service 192.168.1.101 8086"
    echo "  $0 apply"
}

load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    else
        print_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
}

show_current_config() {
    load_config
    
    print_status "Current NGINX Gateway Configuration:"
    echo "====================================="
    echo ""
    echo "Backend Services:"
    echo "  User Service:      ${USER_SERVICE_HOST}:${USER_SERVICE_PORT}"
    echo "  Course Service:    ${COURSE_SERVICE_HOST}:${COURSE_SERVICE_PORT}"
    echo "  Common Service:    ${COMMON_SERVICE_HOST}:${COMMON_SERVICE_PORT}"
    echo "  LTI Service:       ${LTI_SERVICE_HOST}:${LTI_SERVICE_PORT}"
    echo "  Discovery Service: ${DISCOVERY_SERVICE_HOST}:${DISCOVERY_SERVICE_PORT}"
    echo ""
    echo "Frontend:"
    echo "  Frontend:          ${FRONTEND_HOST}:${FRONTEND_PORT}"
    echo ""
    echo "Gateway:"
    echo "  Domain:            ${DOMAIN_NAME}"
    echo "  Server IP:         ${SERVER_IP}"
    echo ""
}

update_interactive() {
    print_status "Interactive IP Configuration Update"
    echo "=================================="
    echo ""
    
    load_config
    
    # User Service
    echo -n "User Service IP [${USER_SERVICE_HOST}]: "
    read -r new_user_host
    new_user_host=${new_user_host:-$USER_SERVICE_HOST}
    
    echo -n "User Service Port [${USER_SERVICE_PORT}]: "
    read -r new_user_port
    new_user_port=${new_user_port:-$USER_SERVICE_PORT}
    
    # Course Service
    echo -n "Course Service IP [${COURSE_SERVICE_HOST}]: "
    read -r new_course_host
    new_course_host=${new_course_host:-$COURSE_SERVICE_HOST}
    
    echo -n "Course Service Port [${COURSE_SERVICE_PORT}]: "
    read -r new_course_port
    new_course_port=${new_course_port:-$COURSE_SERVICE_PORT}
    
    # Common Service
    echo -n "Common Service IP [${COMMON_SERVICE_HOST}]: "
    read -r new_common_host
    new_common_host=${new_common_host:-$COMMON_SERVICE_HOST}
    
    echo -n "Common Service Port [${COMMON_SERVICE_PORT}]: "
    read -r new_common_port
    new_common_port=${new_common_port:-$COMMON_SERVICE_PORT}
    
    # LTI Service
    echo -n "LTI Service IP [${LTI_SERVICE_HOST}]: "
    read -r new_lti_host
    new_lti_host=${new_lti_host:-$LTI_SERVICE_HOST}
    
    echo -n "LTI Service Port [${LTI_SERVICE_PORT}]: "
    read -r new_lti_port
    new_lti_port=${new_lti_port:-$LTI_SERVICE_PORT}
    
    # Frontend
    echo -n "Frontend IP [${FRONTEND_HOST}]: "
    read -r new_frontend_host
    new_frontend_host=${new_frontend_host:-$FRONTEND_HOST}
    
    echo -n "Frontend Port [${FRONTEND_PORT}]: "
    read -r new_frontend_port
    new_frontend_port=${new_frontend_port:-$FRONTEND_PORT}
    
    # Domain
    echo -n "Domain Name [${DOMAIN_NAME}]: "
    read -r new_domain
    new_domain=${new_domain:-$DOMAIN_NAME}
    
    # Update config file
    update_config_file "$new_user_host" "$new_user_port" "$new_course_host" "$new_course_port" \
                      "$new_common_host" "$new_common_port" "$new_lti_host" "$new_lti_port" \
                      "$new_frontend_host" "$new_frontend_port" "$new_domain"
    
    print_success "Configuration updated. Run '$0 apply' to apply changes."
}

auto_detect_ips() {
    print_status "Auto-detecting service IPs..."
    
    # Get current server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    print_status "Detected server IP: ${SERVER_IP}"
    
    # Try to detect services on common ports
    services=(
        "user-service:8086"
        "course-service:8084"
        "common-service:8087"
        "lti-service:8082"
        "discovery-service:8761"
        "frontend:3000"
    )
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        # Check localhost first
        if curl -s --connect-timeout 2 "http://localhost:$port" > /dev/null 2>&1; then
            print_success "Found $service_name on localhost:$port"
            case $service_name in
                "user-service")
                    USER_SERVICE_HOST="127.0.0.1"
                    ;;
                "course-service")
                    COURSE_SERVICE_HOST="127.0.0.1"
                    ;;
                "common-service")
                    COMMON_SERVICE_HOST="127.0.0.1"
                    ;;
                "lti-service")
                    LTI_SERVICE_HOST="127.0.0.1"
                    ;;
                "discovery-service")
                    DISCOVERY_SERVICE_HOST="127.0.0.1"
                    ;;
                "frontend")
                    FRONTEND_HOST="127.0.0.1"
                    ;;
            esac
        else
            print_warning "Service $service_name not found on localhost:$port"
        fi
    done
    
    print_status "Auto-detection complete. Please verify the results and run '$0 apply' if correct."
}

set_service_ip() {
    local service=$1
    local ip=$2
    local port=$3
    
    if [[ -z "$service" || -z "$ip" || -z "$port" ]]; then
        print_error "Usage: $0 set <service> <ip> <port>"
        print_error "Services: user-service, course-service, common-service, lti-service, frontend"
        exit 1
    fi
    
    load_config
    
    case $service in
        "user-service")
            USER_SERVICE_HOST="$ip"
            USER_SERVICE_PORT="$port"
            ;;
        "course-service")
            COURSE_SERVICE_HOST="$ip"
            COURSE_SERVICE_PORT="$port"
            ;;
        "common-service")
            COMMON_SERVICE_HOST="$ip"
            COMMON_SERVICE_PORT="$port"
            ;;
        "lti-service")
            LTI_SERVICE_HOST="$ip"
            LTI_SERVICE_PORT="$port"
            ;;
        "frontend")
            FRONTEND_HOST="$ip"
            FRONTEND_PORT="$port"
            ;;
        *)
            print_error "Unknown service: $service"
            exit 1
            ;;
    esac
    
    update_config_file "$USER_SERVICE_HOST" "$USER_SERVICE_PORT" "$COURSE_SERVICE_HOST" "$COURSE_SERVICE_PORT" \
                      "$COMMON_SERVICE_HOST" "$COMMON_SERVICE_PORT" "$LTI_SERVICE_HOST" "$LTI_SERVICE_PORT" \
                      "$FRONTEND_HOST" "$FRONTEND_PORT" "$DOMAIN_NAME"
    
    print_success "Updated $service to $ip:$port"
}

update_config_file() {
    local user_host=$1
    local user_port=$2
    local course_host=$3
    local course_port=$4
    local common_host=$5
    local common_port=$6
    local lti_host=$7
    local lti_port=$8
    local frontend_host=$9
    local frontend_port=${10}
    local domain=${11}
    
    cat > "$CONFIG_FILE" << EOF
# NGINX Gateway Configuration Variables
# Updated: $(date)

# Backend Services Configuration
export USER_SERVICE_HOST="$user_host"
export USER_SERVICE_PORT="$user_port"

export COURSE_SERVICE_HOST="$course_host"
export COURSE_SERVICE_PORT="$course_port"

export COMMON_SERVICE_HOST="$common_host"
export COMMON_SERVICE_PORT="$common_port"

export LTI_SERVICE_HOST="$lti_host"
export LTI_SERVICE_PORT="$lti_port"

export DISCOVERY_SERVICE_HOST="$DISCOVERY_SERVICE_HOST"
export DISCOVERY_SERVICE_PORT="$DISCOVERY_SERVICE_PORT"

# Frontend Configuration
export FRONTEND_HOST="$frontend_host"
export FRONTEND_PORT="$frontend_port"

# Domain Configuration
export DOMAIN_NAME="$domain"
export SERVER_IP="$SERVER_IP"

# SSL Configuration
export SSL_CERT_PATH="/etc/ssl/certs/nginx-selfsigned.crt"
export SSL_KEY_PATH="/etc/ssl/private/nginx-selfsigned.key"

# Load Balancing Configuration
export ENABLE_LOAD_BALANCING="false"

# Health Check Configuration
export HEALTH_CHECK_INTERVAL="30s"
export HEALTH_CHECK_TIMEOUT="10s"
export HEALTH_CHECK_RETRIES="3"

# Rate Limiting Configuration
export API_RATE_LIMIT="10r/s"
export AUTH_RATE_LIMIT="5r/s"
export API_BURST_LIMIT="20"
export AUTH_BURST_LIMIT="10"

# Monitoring Configuration
export PROMETHEUS_PORT="9090"
export GRAFANA_PORT="3001"
export NGINX_EXPORTER_PORT="9113"

# Logging Configuration
export LOG_LEVEL="warn"
export LOG_FORMAT="main"
export ACCESS_LOG_PATH="/var/log/nginx/access.log"
export ERROR_LOG_PATH="/var/log/nginx/error.log"

echo "NGINX Gateway configuration loaded"
echo "Backend Services:"
echo "  User Service: \${USER_SERVICE_HOST}:\${USER_SERVICE_PORT}"
echo "  Course Service: \${COURSE_SERVICE_HOST}:\${COURSE_SERVICE_PORT}"
echo "  Common Service: \${COMMON_SERVICE_HOST}:\${COMMON_SERVICE_PORT}"
echo "  LTI Service: \${LTI_SERVICE_HOST}:\${LTI_SERVICE_PORT}"
echo "  Frontend: \${FRONTEND_HOST}:\${FRONTEND_PORT}"
echo "Gateway: \${SERVER_IP} (\${DOMAIN_NAME})"
EOF
}

apply_configuration() {
    load_config
    
    print_status "Applying configuration to NGINX files..."
    
    if [[ ! -d "$NGINX_DIR" ]]; then
        print_error "NGINX directory not found: $NGINX_DIR"
        print_error "Please run the deployment script first"
        exit 1
    fi
    
    # Update nginx.conf
    print_status "Updating nginx.conf..."
    sed -i "s/server [0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:8086/server ${USER_SERVICE_HOST}:${USER_SERVICE_PORT}/g" "${NGINX_DIR}/conf/nginx.conf"
    sed -i "s/server [0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:8084/server ${COURSE_SERVICE_HOST}:${COURSE_SERVICE_PORT}/g" "${NGINX_DIR}/conf/nginx.conf"
    sed -i "s/server [0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:8087/server ${COMMON_SERVICE_HOST}:${COMMON_SERVICE_PORT}/g" "${NGINX_DIR}/conf/nginx.conf"
    sed -i "s/server [0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:8082/server ${LTI_SERVICE_HOST}:${LTI_SERVICE_PORT}/g" "${NGINX_DIR}/conf/nginx.conf"
    sed -i "s/server [0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:3000/server ${FRONTEND_HOST}:${FRONTEND_PORT}/g" "${NGINX_DIR}/conf/nginx.conf"
    
    # Update routes.conf
    print_status "Updating routes.conf..."
    sed -i "s/your-domain.com/${DOMAIN_NAME}/g" "${NGINX_DIR}/conf.d/routes.conf"
    
    print_success "Configuration applied successfully!"
    print_warning "Please restart NGINX Gateway to apply changes:"
    print_warning "  sudo systemctl restart nginx-gateway"
    print_warning "  OR"
    print_warning "  ./manage.sh restart"
}

# Main function
main() {
    case "$1" in
        show)
            show_current_config
            ;;
        update)
            update_interactive
            ;;
        auto)
            auto_detect_ips
            ;;
        set)
            set_service_ip "$2" "$3" "$4"
            ;;
        apply)
            apply_configuration
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
