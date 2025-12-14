# Kong Gateway Configuration Script for Windows PowerShell
# This script sets up services, routes, and JWT authentication

$KONG_ADMIN_URL = "http://localhost:8001"

Write-Host "Configuring Kong Gateway..." -ForegroundColor Green

# Function to check if Kong is ready
function Wait-ForKong {
    Write-Host "Waiting for Kong to be ready..." -ForegroundColor Yellow
    do {
        try {
            $response = Invoke-RestMethod -Uri $KONG_ADMIN_URL -Method GET -ErrorAction Stop
            Write-Host "Kong is ready!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "Kong not ready yet, waiting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    } while ($true)
}

# Function to create service
function New-KongService {
    param(
        [string]$ServiceName,
        [string]$ServiceUrl,
        [string]$ServicePath = "/"
    )
    
    Write-Host "Creating service: $ServiceName" -ForegroundColor Cyan
    
    $body = @{
        name = $ServiceName
        url = $ServiceUrl
        path = $ServicePath
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/services" -Method POST -Body $body -ContentType "application/json"
        Write-Host "   Service '$ServiceName' created successfully" -ForegroundColor Green
    } catch {
        Write-Host "   Failed to create service '$ServiceName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to create route
function New-KongRoute {
    param(
        [string]$ServiceName,
        [string]$RoutePath,
        [string]$RouteName
    )
    
    Write-Host "Creating route: $RouteName" -ForegroundColor Cyan
    
    $body = @{
        name = $RouteName
        paths = @($RoutePath)
        methods = @("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/services/$ServiceName/routes" -Method POST -Body $body -ContentType "application/json"
        Write-Host "   Route '$RouteName' created successfully" -ForegroundColor Green
    } catch {
        Write-Host "   Failed to create route '$RouteName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to enable JWT plugin
function Enable-JwtPlugin {
    param([string]$ServiceName)
    
    Write-Host "Enabling JWT plugin for: $ServiceName" -ForegroundColor Cyan
    
    $body = @{
        name = "jwt"
        config = @{
            secret_is_base64 = $false
            key_claim_name = "iss"
            claims_to_verify = @("exp")
        }
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/services/$ServiceName/plugins" -Method POST -Body $body -ContentType "application/json"
        Write-Host "   JWT plugin enabled for '$ServiceName'" -ForegroundColor Green
    } catch {
        Write-Host "   Failed to enable JWT plugin for '$ServiceName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to enable CORS plugin
function Enable-CorsPlugin {
    param([string]$ServiceName)
    
    Write-Host "Enabling CORS plugin for: $ServiceName" -ForegroundColor Cyan
    
    $body = @{
        name = "cors"
        config = @{
            origins = @("*")
            methods = @("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
            headers = @("Accept", "Accept-Version", "Content-Length", "Content-MD5", "Content-Type", "Date", "Authorization")
            exposed_headers = @("X-Auth-Token")
            credentials = $true
            max_age = 3600
        }
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/services/$ServiceName/plugins" -Method POST -Body $body -ContentType "application/json"
        Write-Host "   CORS plugin enabled for '$ServiceName'" -ForegroundColor Green
    } catch {
        Write-Host "   Failed to enable CORS plugin for '$ServiceName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to create JWT consumer
function New-JwtConsumer {
    param(
        [string]$ConsumerName,
        [string]$JwtKey,
        [string]$JwtSecret
    )
    
    Write-Host "Creating JWT consumer: $ConsumerName" -ForegroundColor Cyan
    
    # Create consumer
    $consumerBody = @{
        username = $ConsumerName
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/consumers" -Method POST -Body $consumerBody -ContentType "application/json"
        Write-Host "   Consumer '$ConsumerName' created" -ForegroundColor Green
    } catch {
        Write-Host "   Consumer might already exist: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Add JWT credential
    $jwtBody = @{
        key = $JwtKey
        secret = $JwtSecret
        algorithm = "HS256"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$KONG_ADMIN_URL/consumers/$ConsumerName/jwt" -Method POST -Body $jwtBody -ContentType "application/json"
        Write-Host "   JWT credential added for '$ConsumerName'" -ForegroundColor Green
    } catch {
        Write-Host "   Failed to add JWT credential: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Wait for Kong to be ready
Wait-ForKong

Write-Host "🔧 Setting up services and routes..." -ForegroundColor Blue

# 1. User Service (Authentication - No JWT required for login)
New-KongService "user-service" "http://host.docker.internal:8080" "/api/users"
New-KongRoute "user-service" "/auth/*" "auth-route"
New-KongRoute "user-service" "/api/users/*" "users-route"
Enable-CorsPlugin "user-service"

# 2. Course Service (JWT Protected)
New-KongService "course-service" "http://host.docker.internal:8081" "/api/courses"
New-KongRoute "course-service" "/api/courses/*" "courses-route"
Enable-JwtPlugin "course-service"
Enable-CorsPlugin "course-service"

# 3. LTI Service (Partial JWT Protection) - Local port 8082
New-KongService "lti-service" "http://host.docker.internal:8082" "/"
New-KongRoute "lti-service" "/lti/*" "lti-route"
New-KongRoute "lti-service" "/api/lti/*" "lti-api-route"
Enable-CorsPlugin "lti-service"

# 4. Frontend Service (No JWT needed - static files) - Local port 5173
New-KongService "frontend-service" "http://host.docker.internal:5173" "/"
New-KongRoute "frontend-service" "/" "frontend-route"
Enable-CorsPlugin "frontend-service"

# Create JWT consumer for the application
New-JwtConsumer "adaptive-learning-app" "adaptive-learning-issuer" "your-super-secret-jwt-key-for-kong-gateway-2024"