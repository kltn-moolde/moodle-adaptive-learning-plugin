#!/bin/bash

# NGINX Gateway Management Script
# Provides easy commands to manage the NGINX Gateway

NGINX_DIR="/opt/nginx-gateway"
COMPOSE_FILE="${NGINX_DIR}/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo "NGINX Gateway Management Script"
    echo "==============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start NGINX Gateway"
    echo "  stop        Stop NGINX Gateway"
    echo "  restart     Restart NGINX Gateway"
    echo "  status      Show status of all services"
    echo "  logs        Show logs (use -f for follow)"
    echo "  health      Check health of services"
    echo "  reload      Reload NGINX configuration"
    echo "  update      Update to latest images"
    echo "  backup      Backup configuration"
    echo "  monitor     Open monitoring dashboard"
    echo "  test        Test configuration"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs -f"
    echo "  $0 health"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
}

check_directory() {
    if [[ ! -d "$NGINX_DIR" ]]; then
        print_error "NGINX Gateway directory not found: $NGINX_DIR"
        print_error "Please run the deployment script first"
        exit 1
    fi
    
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
}

start_gateway() {
    print_status "Starting NGINX Gateway..."
    cd "$NGINX_DIR"
    
    if docker-compose up -d; then
        print_success "NGINX Gateway started successfully"
        sleep 5
        check_health
    else
        print_error "Failed to start NGINX Gateway"
        exit 1
    fi
}

stop_gateway() {
    print_status "Stopping NGINX Gateway..."
    cd "$NGINX_DIR"
    
    if docker-compose down; then
        print_success "NGINX Gateway stopped successfully"
    else
        print_error "Failed to stop NGINX Gateway"
        exit 1
    fi
}

restart_gateway() {
    print_status "Restarting NGINX Gateway..."
    stop_gateway
    sleep 2
    start_gateway
}

show_status() {
    print_status "NGINX Gateway Status:"
    cd "$NGINX_DIR"
    docker-compose ps
    
    echo ""
    print_status "System Resources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

show_logs() {
    cd "$NGINX_DIR"
    
    if [[ "$2" == "-f" ]]; then
        print_status "Following logs (Ctrl+C to exit)..."
        docker-compose logs -f
    else
        print_status "Recent logs:"
        docker-compose logs --tail=50
    fi
}

check_health() {
    print_status "Checking service health..."
    
    # Check NGINX Gateway
    if curl -f -s http://localhost/health > /dev/null; then
        print_success "✓ NGINX Gateway: Healthy"
    else
        print_error "✗ NGINX Gateway: Unhealthy"
    fi
    
    # Check Prometheus
    if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
        print_success "✓ Prometheus: Healthy"
    else
        print_warning "✗ Prometheus: Unhealthy"
    fi
    
    # Check Grafana
    if curl -f -s http://localhost:3001/api/health > /dev/null; then
        print_success "✓ Grafana: Healthy"
    else
        print_warning "✗ Grafana: Unhealthy"
    fi
    
    # Check backend services
    print_status "Checking backend services..."
    
    # User Service
    if curl -f -s http://192.168.1.100:8086/actuator/health > /dev/null; then
        print_success "✓ User Service: Healthy"
    else
        print_warning "✗ User Service: Unhealthy or unreachable"
    fi
    
    # Course Service
    if curl -f -s http://192.168.1.100:8084/actuator/health > /dev/null; then
        print_success "✓ Course Service: Healthy"
    else
        print_warning "✗ Course Service: Unhealthy or unreachable"
    fi
    
    # Common Service
    if curl -f -s http://192.168.1.100:8087/actuator/health > /dev/null; then
        print_success "✓ Common Service: Healthy"
    else
        print_warning "✗ Common Service: Unhealthy or unreachable"
    fi
    
    # LTI Service
    if curl -f -s http://192.168.1.100:8082/actuator/health > /dev/null; then
        print_success "✓ LTI Service: Healthy"
    else
        print_warning "✗ LTI Service: Unhealthy or unreachable"
    fi
    
    # Frontend
    if curl -f -s http://192.168.1.200:3000 > /dev/null; then
        print_success "✓ Frontend: Healthy"
    else
        print_warning "✗ Frontend: Unhealthy or unreachable"
    fi
}

reload_nginx() {
    print_status "Reloading NGINX configuration..."
    cd "$NGINX_DIR"
    
    if docker-compose exec nginx-gateway nginx -t; then
        print_success "Configuration test passed"
        if docker-compose exec nginx-gateway nginx -s reload; then
            print_success "NGINX configuration reloaded successfully"
        else
            print_error "Failed to reload NGINX configuration"
        fi
    else
        print_error "Configuration test failed"
        exit 1
    fi
}

update_images() {
    print_status "Updating Docker images..."
    cd "$NGINX_DIR"
    
    if docker-compose pull; then
        print_success "Images updated successfully"
        print_status "Restart the gateway to use new images: $0 restart"
    else
        print_error "Failed to update images"
        exit 1
    fi
}

backup_config() {
    BACKUP_DIR="/opt/nginx-gateway-backup-$(date +%Y%m%d-%H%M%S)"
    
    print_status "Creating backup at: $BACKUP_DIR"
    
    if cp -r "$NGINX_DIR" "$BACKUP_DIR"; then
        print_success "Configuration backed up to: $BACKUP_DIR"
    else
        print_error "Failed to create backup"
        exit 1
    fi
}

open_monitoring() {
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    print_status "Monitoring URLs:"
    echo "  Prometheus: http://$SERVER_IP:9090"
    echo "  Grafana: http://$SERVER_IP:3001 (admin/admin123)"
    echo "  NGINX Status: http://$SERVER_IP/nginx_status"
    echo ""
    
    if command -v xdg-open &> /dev/null; then
        print_status "Opening Grafana in browser..."
        xdg-open "http://$SERVER_IP:3001"
    fi
}

test_config() {
    print_status "Testing NGINX configuration..."
    cd "$NGINX_DIR"
    
    if docker-compose exec nginx-gateway nginx -t; then
        print_success "✓ NGINX configuration is valid"
    else
        print_error "✗ NGINX configuration has errors"
        exit 1
    fi
    
    print_status "Testing connectivity to backend services..."
    check_health
}

# Main function
main() {
    case "$1" in
        start)
            check_docker
            check_directory
            start_gateway
            ;;
        stop)
            check_docker
            check_directory
            stop_gateway
            ;;
        restart)
            check_docker
            check_directory
            restart_gateway
            ;;
        status)
            check_docker
            check_directory
            show_status
            ;;
        logs)
            check_docker
            check_directory
            show_logs "$@"
            ;;
        health)
            check_health
            ;;
        reload)
            check_docker
            check_directory
            reload_nginx
            ;;
        update)
            check_docker
            check_directory
            update_images
            ;;
        backup)
            check_directory
            backup_config
            ;;
        monitor)
            open_monitoring
            ;;
        test)
            check_docker
            check_directory
            test_config
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

# Run main function with all arguments
main "$@"
