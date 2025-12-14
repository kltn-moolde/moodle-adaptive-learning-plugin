#!/bin/bash

# Kong Gateway Configuration Script
# This script sets up services, routes, and JWT authentication

KONG_ADMIN_URL="http://localhost:8001"

echo "🚀 Configuring Kong Gateway..."

# Function to check if Kong is ready
wait_for_kong() {
    echo "Waiting for Kong to be ready..."
    while ! curl -s "$KONG_ADMIN_URL" > /dev/null; do
        echo "Kong not ready yet, waiting..."
        sleep 5
    done
    echo "✅ Kong is ready!"
}

# Function to create service
create_service() {
    local service_name="$1"
    local service_url="$2"
    local service_path="$3"
    
    echo "📦 Creating service: $service_name"
    
    curl -X POST "$KONG_ADMIN_URL/services" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$service_name\",
            \"url\": \"$service_url\",
            \"path\": \"$service_path\"
        }"
    echo ""
}

# Function to create route
create_route() {
    local service_name="$1"
    local route_path="$2"
    local route_name="$3"
    
    echo "🛣️  Creating route: $route_name"
    
    curl -X POST "$KONG_ADMIN_URL/services/$service_name/routes" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$route_name\",
            \"paths\": [\"$route_path\"],
            \"methods\": [\"GET\", \"POST\", \"PUT\", \"DELETE\", \"PATCH\", \"OPTIONS\"]
        }"
    echo ""
}

# Function to enable JWT plugin
enable_jwt_plugin() {
    local service_name="$1"
    
    echo "🔐 Enabling JWT plugin for: $service_name"
    
    curl -X POST "$KONG_ADMIN_URL/services/$service_name/plugins" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"jwt\",
            \"config\": {
                \"secret_is_base64\": false,
                \"key_claim_name\": \"iss\",
                \"claims_to_verify\": [\"exp\"]
            }
        }"
    echo ""
}

# Function to enable CORS plugin
enable_cors_plugin() {
    local service_name="$1"
    
    echo "🌐 Enabling CORS plugin for: $service_name"
    
    curl -X POST "$KONG_ADMIN_URL/services/$service_name/plugins" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"cors\",
            \"config\": {
                \"origins\": [\"*\"],
                \"methods\": [\"GET\", \"POST\", \"PUT\", \"DELETE\", \"PATCH\", \"OPTIONS\"],
                \"headers\": [\"Accept\", \"Accept-Version\", \"Content-Length\", \"Content-MD5\", \"Content-Type\", \"Date\", \"Authorization\"],
                \"exposed_headers\": [\"X-Auth-Token\"],
                \"credentials\": true,
                \"max_age\": 3600
            }
        }"
    echo ""
}

# Function to create JWT consumer
create_jwt_consumer() {
    local consumer_name="$1"
    local jwt_key="$2"
    local jwt_secret="$3"
    
    echo "👤 Creating JWT consumer: $consumer_name"
    
    # Create consumer
    curl -X POST "$KONG_ADMIN_URL/consumers" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$consumer_name\"
        }"
    
    # Add JWT credential
    curl -X POST "$KONG_ADMIN_URL/consumers/$consumer_name/jwt" \
        -H "Content-Type: application/json" \
        -d "{
            \"key\": \"$jwt_key\",
            \"secret\": \"$jwt_secret\",
            \"algorithm\": \"HS256\"
        }"
    echo ""
}

# Wait for Kong to be ready
wait_for_kong

echo "🔧 Setting up services and routes..."

# 1. User Service (Authentication - No JWT required for login)
create_service "user-service" "http://user-service:8080" "/api/users"
create_route "user-service" "/auth/*" "auth-route"
create_route "user-service" "/api/users/*" "users-route"
enable_cors_plugin "user-service"

# 2. Course Service (JWT Protected)
create_service "course-service" "http://course-service:8081" "/api/courses"
create_route "course-service" "/api/courses/*" "courses-route"
enable_jwt_plugin "course-service"
enable_cors_plugin "course-service"

# 3. LTI Service (Partial JWT Protection)
create_service "lti-service" "http://lti-service:8082" "/"
create_route "lti-service" "/lti/*" "lti-route"
create_route "lti-service" "/api/lti/*" "lti-api-route"
# Note: LTI endpoints don't need JWT, but API endpoints do
enable_cors_plugin "lti-service"

# 4. Frontend Service (No JWT needed - static files)
create_service "frontend-service" "http://frontend-service:3000" "/"
create_route "frontend-service" "/" "frontend-route"
enable_cors_plugin "frontend-service"

# Create JWT consumer for the application
create_jwt_consumer "adaptive-learning-app" "adaptive-learning-issuer" "your-super-secret-jwt-key-for-kong-gateway-2024"

echo ""
echo "✅ Kong Gateway configuration completed!"
echo ""
echo "📋 Gateway Endpoints:"
echo "   🌐 Proxy (HTTP):    http://localhost:8000"
echo "   🔒 Proxy (HTTPS):   https://localhost:8443"
echo "   ⚙️  Admin API:       http://localhost:8001"
echo "   🎨 Admin GUI:        http://localhost:8002"
echo "   📊 Konga UI:         http://localhost:1337"
echo ""
echo "🛣️  Service Routes:"
echo "   🔐 Auth:             http://localhost:8000/auth/*"
echo "   👥 Users:            http://localhost:8000/api/users/*"
echo "   📚 Courses:          http://localhost:8000/api/courses/*"
echo "   🎓 LTI:              http://localhost:8000/lti/*"
echo "   📱 Frontend:         http://localhost:8000/"
echo ""
echo "🔑 JWT Configuration:"
echo "   Issuer: adaptive-learning-issuer"
echo "   Algorithm: HS256"
echo "   Header: Authorization: Bearer <token>"
echo ""
