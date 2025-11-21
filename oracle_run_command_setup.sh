#!/bin/bash
# Oracle Cloud Run Command - Initial Setup Script
# This script prepares your instance for deployment

set -e

echo "=== Music Sync App - Oracle Cloud Setup ==="
echo "Starting at $(date)"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    sudo systemctl enable docker
    sudo systemctl start docker
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Install required tools
echo "🔧 Installing utilities..."
sudo apt-get install -y wget curl unzip nano

# Fix SSH if needed - Change SSH to port 2222
echo "🔐 Configuring SSH on port 2222..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Backup SSH config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Change SSH port to 2222
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo sed -i 's/^Port 22/Port 2222/' /etc/ssh/sshd_config

# Add Port 2222 if neither exists
if ! sudo grep -q "^Port 2222" /etc/ssh/sshd_config && ! sudo grep -q "^#Port 22" /etc/ssh/sshd_config; then
    echo "Port 2222" | sudo tee -a /etc/ssh/sshd_config
fi

# Restart SSH service
sudo systemctl restart ssh
sudo systemctl status ssh --no-pager

echo "✅ SSH now running on port 2222"

# Check firewall
echo "🔥 Checking local firewall..."
sudo iptables -L INPUT -n | grep -q "dpt:22" || sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -L INPUT -n | grep -q "dpt:2222" || sudo iptables -I INPUT -p tcp --dport 2222 -j ACCEPT
sudo iptables -L INPUT -n | grep -q "dpt:80" || sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -L INPUT -n | grep -q "dpt:443" || sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -L INPUT -n | grep -q "dpt:3000" || sudo iptables -I INPUT -p tcp --dport 3000 -j ACCEPT

# Make iptables rules persistent
echo "💾 Making firewall rules persistent..."
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save

# Create app directory
echo "📁 Creating application directory..."
mkdir -p /home/ubuntu/music-sync-app
cd /home/ubuntu/music-sync-app

# Create a placeholder for the deployment package
echo "📝 Creating placeholder for deployment package..."
cat > /home/ubuntu/NEXT_STEPS.txt << 'EOL'
=== Next Steps ===

Your instance is now ready! Here's what to do next:

1. Upload the deployment package using one of these methods:

   METHOD A: Via wget (recommended)
   ---------------------------------
   On your Mac, run:
   cd /Users/Ayan/Documents/spotify_to_ytmusic
   python3 -m http.server 8000
   
   Then in another terminal:
   brew install ngrok
   ngrok http 8000
   
   Copy the HTTPS URL from ngrok (e.g., https://xxxx.ngrok-free.app)
   
   Then use Oracle Run Command to execute:
   cd /home/ubuntu/music-sync-app
   wget https://YOUR-NGROK-URL/music-sync-deploy.tar.gz
   tar -xzf music-sync-deploy.tar.gz
   

   METHOD B: Via SCP (SSH now on port 2222)
   -----------------------------------
   From your Mac:
   scp -P 2222 -i /Users/Ayan/Downloads/key2.key music-sync-deploy.tar.gz ubuntu@140.245.21.42:~/music-sync-app/
   
   To SSH into server:
   ssh -p 2222 -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.21.42


2. Configure the environment:
   nano /home/ubuntu/music-sync-app/.env
   
   Add your credentials:
   SECRET_KEY=your_secret_key_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret


3. Deploy the application:
   cd /home/ubuntu/music-sync-app
   chmod +x deploy.sh
   ./deploy.sh


4. Access your app at:
   http://140.245.30.241:3000

EOL

# Display summary
echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"
echo ""
echo "📄 Next steps written to: /home/ubuntu/NEXT_STEPS.txt"
echo ""
echo "View next steps with: cat /home/ubuntu/NEXT_STEPS.txt"
echo ""
echo "Instance is ready for deployment!"
echo ""
echo "⚠️  IMPORTANT: SSH is now on PORT 2222"
echo "   Connect with: ssh -p 2222 -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.21.42"
echo ""
echo "📝 Don't forget to add port 2222 to Oracle Cloud Security List:"
echo "   Source: 0.0.0.0/0, Protocol: TCP, Port: 2222"
echo "========================================"
