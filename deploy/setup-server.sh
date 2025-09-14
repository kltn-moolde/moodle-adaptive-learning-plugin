#!/bin/bash
# Server Setup Script for Adaptive Learning Platform
# Run this script on a fresh Ubuntu/Debian server

set -e

echo "🚀 Setting up Adaptive Learning Platform Server..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y curl git nginx certbot python3-certbot-nginx ufw

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/adaptive-learning
sudo chown $USER:$USER /opt/adaptive-learning

# Clone repository
echo "📥 Cloning repository..."
cd /opt/adaptive-learning
if [ ! -d .git ]; then
    git clone https://github.com/LocNguyenSGU/moodle-adaptive-learning-plugin.git .
else
    git pull origin main
fi

# Setup environment file
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.production .env
    echo "⚠️  Please edit .env file with your production values"
fi

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 8080
sudo ufw allow 8082
sudo ufw allow 5173
sudo ufw --force enable

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/adaptive-learning
sudo ln -sf /etc/nginx/sites-available/adaptive-learning /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# Create systemd service for auto-start
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/adaptive-learning.service > /dev/null <<EOF
[Unit]
Description=Adaptive Learning Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/adaptive-learning
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable adaptive-learning

echo "✅ Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/adaptive-learning/.env with your production values"
echo "2. Update docker-compose.prod.yml with your Docker Hub username"
echo "3. Run: sudo systemctl start adaptive-learning"
echo "4. Setup SSL: sudo certbot --nginx -d your-domain.com"
echo ""
echo "🔗 Services will be available at:"
echo "   - Frontend: http://51.68.124.207:5173"
echo "   - API Gateway: http://51.68.124.207:8000"
echo "   - User Service: http://51.68.124.207:8080"
echo "   - LTI Service: http://51.68.124.207:8082"