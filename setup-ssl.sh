#!/bin/bash
# Setup SSL/HTTPS with Let's Encrypt
# Run this on your Oracle Cloud server

set -e

echo "=== SSL/HTTPS Setup for Music Sync App ==="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./setup-ssl.sh"
    exit 1
fi

# Prompt for domain name
read -p "Enter your domain name (e.g., musicsync.example.com): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Domain name is required!"
    echo ""
    echo "IMPORTANT: You need a domain name for HTTPS."
    echo "Options:"
    echo "1. Buy a domain from Namecheap, GoDaddy, etc."
    echo "2. Use a free subdomain from FreeDNS, NoIP, etc."
    echo "3. Point your domain's A record to: 140.245.30.241"
    exit 1
fi

read -p "Enter your email for SSL certificate notifications: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "❌ Email is required!"
    exit 1
fi

echo ""
echo "📋 Configuration:"
echo "   Domain: $DOMAIN_NAME"
echo "   Email: $EMAIL"
echo "   Server IP: 140.245.30.241"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Install Certbot
echo "📦 Installing Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Stop the app temporarily to free port 80
echo "⏸️  Stopping app temporarily..."
cd /home/ubuntu
docker-compose down

# Get SSL certificate
echo "🔐 Obtaining SSL certificate..."
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN_NAME"

# Create nginx configuration for HTTPS
echo "⚙️  Configuring Nginx for HTTPS..."
cat > /home/ubuntu/nginx-ssl.conf << EOF
events {
    worker_connections 1024;
}

http {
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN_NAME;
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN_NAME;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options SAMEORIGIN;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Proxy to Flask app
        location / {
            proxy_pass http://web:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts for long-running sync operations
            proxy_connect_timeout 600s;
            proxy_send_timeout 600s;
            proxy_read_timeout 600s;
        }

        # Static files
        location /static {
            proxy_pass http://web:5000/static;
        }
    }
}
EOF

# Update docker-compose.yml to include Nginx
echo "🐳 Updating Docker Compose configuration..."
cat > /home/ubuntu/docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    container_name: music_sync_app
    restart: unless-stopped
    expose:
      - "5000"
    volumes:
      - ./data:/app/data
      - ./backups:/app/backups
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - DATABASE_PATH=/app/data/music_sync.db
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: music_sync_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
EOF

# Open firewall ports
echo "🔥 Opening firewall ports..."
iptables -I INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
netfilter-persistent save

# Start the app with HTTPS
echo "🚀 Starting app with HTTPS..."
cd /home/ubuntu
docker-compose up -d

# Wait for services to start
sleep 10

# Setup auto-renewal
echo "🔄 Setting up SSL certificate auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

# Create renewal hook to reload nginx
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'HOOK'
#!/bin/bash
cd /home/ubuntu && docker-compose restart nginx
HOOK
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh

echo ""
echo "========================================"
echo "✅ HTTPS Setup Complete!"
echo "========================================"
echo ""
echo "🌐 Your app is now accessible at:"
echo "   https://$DOMAIN_NAME"
echo ""
echo "🔒 SSL Certificate Details:"
echo "   Domain: $DOMAIN_NAME"
echo "   Valid for: 90 days"
echo "   Auto-renewal: Enabled"
echo ""
echo "📝 Next Steps:"
echo "1. Update Spotify Redirect URI to:"
echo "   https://$DOMAIN_NAME/spotify/callback"
echo ""
echo "2. Test your site:"
echo "   curl -I https://$DOMAIN_NAME"
echo ""
echo "3. Check SSL grade at:"
echo "   https://www.ssllabs.com/ssltest/"
echo ""
echo "========================================"
