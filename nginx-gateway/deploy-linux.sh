#!/bin/bash

# NGINX Gateway Deployment Script for Linux
# This script sets up and starts the NGINX Gateway on Linux

set -e

echo "🚀 Starting NGINX Gateway deployment on Linux..."

# Configuration
NGINX_DIR="/opt/nginx-gateway"
SSL_DIR="/etc/ssl/nginx"
DOMAIN="your-domain.com"  # Change this to your domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Install required packages
install_dependencies() {
    print_status "Installing required packages..."
    
    # Update package lists
    apt-get update
    
    # Install Docker and Docker Compose
    if ! command -v docker &> /dev/null; then
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
        rm get-docker.sh
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_status "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Install curl for health checks
    apt-get install -y curl openssl
    
    print_success "Dependencies installed successfully"
}

# Create SSL certificates
create_ssl_certificates() {
    print_status "Creating SSL certificates..."
    
    mkdir -p ${SSL_DIR}/certs
    mkdir -p ${SSL_DIR}/private
    
    if [[ ! -f "${SSL_DIR}/certs/nginx-selfsigned.crt" ]]; then
        print_status "Generating self-signed SSL certificate..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ${SSL_DIR}/private/nginx-selfsigned.key \
            -out ${SSL_DIR}/certs/nginx-selfsigned.crt \
            -subj "/C=VN/ST=Ho Chi Minh/L=Ho Chi Minh/O=Organization/OU=OrgUnit/CN=${DOMAIN}"
        
        chmod 600 ${SSL_DIR}/private/nginx-selfsigned.key
        chmod 644 ${SSL_DIR}/certs/nginx-selfsigned.crt
        
        print_success "SSL certificates created"
    else
        print_warning "SSL certificates already exist"
    fi
}

# Create nginx gateway directory
setup_nginx_directory() {
    print_status "Setting up NGINX Gateway directory..."
    
    # Create directory if it doesn't exist
    mkdir -p ${NGINX_DIR}
    
    # Copy configuration files
    if [[ -d "./conf" ]]; then
        cp -r ./conf ${NGINX_DIR}/
        cp -r ./conf.d ${NGINX_DIR}/
        cp docker-compose.yml ${NGINX_DIR}/
        
        # Create logs directory
        mkdir -p ${NGINX_DIR}/logs
        
        # Create monitoring directory
        mkdir -p ${NGINX_DIR}/monitoring
        
        print_success "NGINX Gateway directory setup complete"
    else
        print_error "Configuration files not found in current directory"
        exit 1
    fi
}

# Create monitoring configuration
setup_monitoring() {
    print_status "Setting up monitoring configuration..."
    
    # Prometheus configuration
    cat > ${NGINX_DIR}/monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'node'
    static_configs:
      - targets: ['host.docker.internal:9100']

  # Add your microservices here
  - job_name: 'user-service'
    static_configs:
      - targets: ['192.168.1.100:8086']

  - job_name: 'course-service'
    static_configs:
      - targets: ['192.168.1.100:8084']

  - job_name: 'common-service'
    static_configs:
      - targets: ['192.168.1.100:8087']

  - job_name: 'lti-service'
    static_configs:
      - targets: ['192.168.1.100:8082']
EOF

    # Grafana datasource configuration
    mkdir -p ${NGINX_DIR}/monitoring/grafana/datasources
    cat > ${NGINX_DIR}/monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    # Grafana dashboard configuration
    mkdir -p ${NGINX_DIR}/monitoring/grafana/dashboards
    cat > ${NGINX_DIR}/monitoring/grafana/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    print_success "Monitoring configuration created"
}

# Update IP addresses in configuration
update_ip_addresses() {
    print_status "Updating IP addresses in configuration..."
    
    # Get current server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    print_status "Detected server IP: ${SERVER_IP}"
    
    # Update routes.conf with correct domain
    sed -i "s/your-domain.com/${DOMAIN}/g" ${NGINX_DIR}/conf.d/routes.conf
    
    print_status "Please update the IP addresses in ${NGINX_DIR}/conf/nginx.conf"
    print_status "Current backend service IPs are set to:"
    print_status "  - User Service: 192.168.1.100:8086"
    print_status "  - Course Service: 192.168.1.100:8084"
    print_status "  - Common Service: 192.168.1.100:8087"
    print_status "  - LTI Service: 192.168.1.100:8082"
    print_status "  - Frontend: 192.168.1.200:3000"
    
    print_warning "Please update these IPs to match your actual service locations!"
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw --force enable
        ufw allow 22/tcp      # SSH
        ufw allow 80/tcp      # HTTP
        ufw allow 443/tcp     # HTTPS
        ufw allow 9090/tcp    # Prometheus
        ufw allow 3001/tcp    # Grafana
        print_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=9090/tcp
        firewall-cmd --permanent --add-port=3001/tcp
        firewall-cmd --reload
        print_success "Firewalld configured"
    else
        print_warning "No firewall manager found. Please configure firewall manually."
    fi
}

# Start NGINX Gateway
start_gateway() {
    print_status "Starting NGINX Gateway..."
    
    cd ${NGINX_DIR}
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to start
    sleep 10
    
    # Check health
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "NGINX Gateway started successfully!"
        print_success "Gateway is running on: http://${DOMAIN}"
        print_success "HTTPS: https://${DOMAIN}"
        print_success "Prometheus: http://${DOMAIN}:9090"
        print_success "Grafana: http://${DOMAIN}:3001 (admin/admin123)"
    else
        print_error "NGINX Gateway failed to start properly"
        print_status "Checking logs..."
        docker-compose logs nginx-gateway
        exit 1
    fi
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > /etc/systemd/system/nginx-gateway.service << EOF
[Unit]
Description=NGINX Gateway Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${NGINX_DIR}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable nginx-gateway
    
    print_success "Systemd service created and enabled"
}

# Main deployment function
main() {
    print_status "NGINX Gateway Deployment for Linux"
    print_status "=================================="
    
    check_root
    install_dependencies
    create_ssl_certificates
    setup_nginx_directory
    setup_monitoring
    update_ip_addresses
    configure_firewall
    start_gateway
    create_systemd_service
    
    echo ""
    print_success "🎉 NGINX Gateway deployment completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Update IP addresses in ${NGINX_DIR}/conf/nginx.conf"
    echo "2. Replace self-signed certificates with real ones if needed"
    echo "3. Update domain name in ${NGINX_DIR}/conf.d/routes.conf"
    echo "4. Test your microservices connectivity"
    echo ""
    print_status "Service management commands:"
    echo "  - Start: systemctl start nginx-gateway"
    echo "  - Stop: systemctl stop nginx-gateway"
    echo "  - Status: systemctl status nginx-gateway"
    echo "  - Logs: docker-compose -f ${NGINX_DIR}/docker-compose.yml logs"
    echo ""
}

# Run main function
main "$@"
