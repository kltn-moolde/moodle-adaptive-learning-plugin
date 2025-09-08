#!/bin/bash
# Eureka Service Discovery Integration Script
# Automatically updates NGINX upstream configuration based on Eureka registry

EUREKA_URL="http://localhost:8761/eureka/apps"
NGINX_CONF_DIR="./conf"
NGINX_UPSTREAM_FILE="$NGINX_CONF_DIR/dynamic-upstreams.conf"
NGINX_PID_FILE="./logs/nginx.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Fetch service instances from Eureka
fetch_services() {
    log "Fetching services from Eureka..."
    
    # Get services JSON from Eureka
    SERVICES_JSON=$(curl -s -H "Accept: application/json" "$EUREKA_URL" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        error "Failed to connect to Eureka at $EUREKA_URL"
        return 1
    fi
    
    echo "$SERVICES_JSON"
}

# Parse service instances and generate NGINX upstream config
generate_upstream_config() {
    local services_json="$1"
    local config_file="$2"
    
    log "Generating NGINX upstream configuration..."
    
    # Start config file
    cat > "$config_file" << EOF
# Auto-generated upstream configuration from Eureka
# Generated at: $(date)
# DO NOT EDIT MANUALLY - This file is auto-generated

EOF

    # Parse each service
    echo "$services_json" | jq -r '.applications.application[]' 2>/dev/null | while read -r app; do
        SERVICE_NAME=$(echo "$app" | jq -r '.name' | tr '[:upper:]' '[:lower:]' 2>/dev/null)
        
        if [ "$SERVICE_NAME" != "null" ] && [ "$SERVICE_NAME" != "GATEWAYSERVICE" ] && [ "$SERVICE_NAME" != "DISCOVERYSERVICE" ]; then
            log "Processing service: $SERVICE_NAME"
            
            # Start upstream block
            echo "upstream ${SERVICE_NAME}-cluster {" >> "$config_file"
            echo "    least_conn;" >> "$config_file"
            
            # Get instances
            INSTANCES=$(echo "$app" | jq -r '.instance[]?' 2>/dev/null)
            
            if [ -n "$INSTANCES" ]; then
                echo "$INSTANCES" | while read -r instance; do
                    IP=$(echo "$instance" | jq -r '.ipAddr // .hostName' 2>/dev/null)
                    PORT=$(echo "$instance" | jq -r '.port."$"' 2>/dev/null)
                    STATUS=$(echo "$instance" | jq -r '.status' 2>/dev/null)
                    
                    if [ "$STATUS" = "UP" ] && [ "$IP" != "null" ] && [ "$PORT" != "null" ]; then
                        echo "    server $IP:$PORT max_fails=3 fail_timeout=30s weight=1;" >> "$config_file"
                        log "  Added server: $IP:$PORT"
                    fi
                done
            fi
            
            # End upstream block
            echo "    keepalive 32;" >> "$config_file"
            echo "    keepalive_requests 100;" >> "$config_file"
            echo "    keepalive_timeout 60s;" >> "$config_file"
            echo "}" >> "$config_file"
            echo "" >> "$config_file"
        fi
    done
    
    log "Upstream configuration generated: $config_file"
}

# Test NGINX configuration
test_nginx_config() {
    log "Testing NGINX configuration..."
    
    if nginx -t -c "$NGINX_CONF_DIR/nginx.conf" >/dev/null 2>&1; then
        log "NGINX configuration test passed"
        return 0
    else
        error "NGINX configuration test failed"
        nginx -t -c "$NGINX_CONF_DIR/nginx.conf"
        return 1
    fi
}

# Reload NGINX
reload_nginx() {
    log "Reloading NGINX..."
    
    if [ -f "$NGINX_PID_FILE" ]; then
        if nginx -s reload 2>/dev/null; then
            log "NGINX reloaded successfully"
            return 0
        else
            error "Failed to reload NGINX"
            return 1
        fi
    else
        warn "NGINX PID file not found. NGINX may not be running."
        return 1
    fi
}

# Main execution
main() {
    log "Starting Eureka service discovery sync..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$NGINX_PID_FILE")"
    
    # Fetch services from Eureka
    SERVICES=$(fetch_services)
    if [ $? -ne 0 ]; then
        error "Failed to fetch services from Eureka"
        exit 1
    fi
    
    # Generate backup of current config
    if [ -f "$NGINX_UPSTREAM_FILE" ]; then
        cp "$NGINX_UPSTREAM_FILE" "${NGINX_UPSTREAM_FILE}.backup.$(date +%s)"
    fi
    
    # Generate new upstream configuration
    generate_upstream_config "$SERVICES" "$NGINX_UPSTREAM_FILE"
    
    # Test configuration
    if test_nginx_config; then
        # Reload NGINX if test passes
        if reload_nginx; then
            log "Eureka sync completed successfully"
        else
            warn "Configuration updated but NGINX reload failed"
        fi
    else
        error "Configuration test failed. Rolling back..."
        if [ -f "${NGINX_UPSTREAM_FILE}.backup.*" ]; then
            mv "${NGINX_UPSTREAM_FILE}.backup."* "$NGINX_UPSTREAM_FILE"
            log "Configuration rolled back"
        fi
        exit 1
    fi
}

# Run continuously if --watch flag is provided
if [ "$1" = "--watch" ]; then
    log "Starting continuous monitoring mode..."
    while true; do
        main
        log "Waiting 30 seconds before next sync..."
        sleep 30
    done
else
    main
fi
