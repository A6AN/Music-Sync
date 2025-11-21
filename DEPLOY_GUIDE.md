# 🚀 Deployment Guide for Oracle Cloud

Complete guide to deploy Music Sync Pro on Oracle Cloud.

## 📋 Prerequisites

1. Oracle Cloud account with a compute instance running
2. Ubuntu 20.04+ or similar Linux distribution
3. SSH access to your server
4. Domain name (optional, but recommended)

## 🔧 Initial Server Setup

### 1. Connect to Your Oracle Cloud Instance

```bash
ssh ubuntu@your-server-ip
```

### 2. Update System and Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git curl wget nano

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and back in for docker group to take effect
exit
```

### 3. Configure Oracle Cloud Firewall

```bash
# On your Oracle Cloud instance
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Or if using iptables
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

**Also configure in Oracle Cloud Console:**
1. Go to Oracle Cloud Console → Networking → Virtual Cloud Networks
2. Select your VCN → Security Lists
3. Add Ingress Rules:
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 8080 (Flask app)
   - Source: 0.0.0.0/0

## 📦 Deploy the Application

### 1. Clone or Upload Your Project

**Option A: Using Git (Recommended)**
```bash
cd ~
git clone https://github.com/yourusername/spotify_to_ytmusic.git
cd spotify_to_ytmusic
```

**Option B: Upload Files (Manual)**
```bash
# On your local machine
cd /Users/Ayan/Documents/spotify_to_ytmusic
tar -czf music-sync.tar.gz --exclude='.git' --exclude='*.db' --exclude='__pycache__' --exclude='*.pyc' .

# Upload to server
scp music-sync.tar.gz ubuntu@your-server-ip:~/

# On server
mkdir -p ~/spotify_to_ytmusic
cd ~/spotify_to_ytmusic
tar -xzf ~/music-sync.tar.gz
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Generate a new secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env

# Edit the .env file
nano .env
```

**Important: Update these values in .env:**
```bash
SECRET_KEY=your_generated_secret_key_here
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
FLASK_ENV=production
FLASK_HOST=0.0.0.0
```

**Update Spotify Redirect URI:**
Go to https://developer.spotify.com/dashboard
- Add redirect URI: `http://your-server-ip:8080/spotify/callback`
- Or with domain: `https://your-domain.com/spotify/callback`

### 3. Make Scripts Executable

```bash
chmod +x deploy.sh backup.sh restore.sh setup-cron.sh
```

### 4. Deploy the Application

```bash
./deploy.sh
```

The script will:
- Create necessary directories
- Build Docker image
- Start the application
- Show status and useful commands

### 5. Verify Deployment

```bash
# Check if container is running
docker ps

# View logs
docker-compose logs -f

# Test the application
curl http://localhost:8080
```

Access your app at: `http://your-server-ip:8080`

## 🔒 Setup Nginx Reverse Proxy (Recommended)

### 1. Install Nginx

```bash
sudo apt install -y nginx
```

### 2. Configure Nginx

```bash
# Copy the nginx config
sudo cp nginx.conf /etc/nginx/sites-available/music-sync

# Edit and replace 'your-domain.com' with your actual domain or IP
sudo nano /etc/nginx/sites-available/music-sync

# Enable the site
sudo ln -s /etc/nginx/sites-available/music-sync /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

Now access your app at: `http://your-domain.com` (port 80)

### 3. Setup SSL with Let's Encrypt (HTTPS)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure HTTPS
```

Now access your app securely at: `https://your-domain.com`

## 💾 Setup Automatic Backups

### 1. Configure Cron for Daily Backups

```bash
./setup-cron.sh
```

This sets up daily backups at 2 AM.

### 2. Manual Backup

```bash
./backup.sh
```

Backups are stored in `./backups/` directory.

### 3. Restore from Backup

```bash
./restore.sh
```

## 🔄 Application Management

### Start Application
```bash
docker-compose up -d
```

### Stop Application
```bash
docker-compose down
```

### Restart Application
```bash
docker-compose restart
```

### View Logs
```bash
docker-compose logs -f
```

### Update Application
```bash
git pull  # If using git
./deploy.sh
```

### Access Container Shell
```bash
docker exec -it music_sync_app bash
```

## 📊 Monitoring

### Check Application Status
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats music_sync_app
```

### Check Disk Space
```bash
df -h
du -sh data/ backups/
```

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Check if port is in use
sudo lsof -i :8080

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues
```bash
# Restore from backup
./restore.sh

# Or reset database (WARNING: deletes all data)
docker-compose down
rm data/music_sync.db
docker-compose up -d
```

### Nginx Issues
```bash
# Check nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Connection Issues
```bash
# Check if firewall is blocking
sudo firewall-cmd --list-all
# or
sudo iptables -L -n

# Check Oracle Cloud security lists in the web console
```

## 🔐 Security Best Practices

1. **Change Default Ports** (optional)
   ```bash
   # Edit docker-compose.yml
   ports:
     - "8080:8080"  # Use different external port
   ```

2. **Setup Firewall Rules**
   ```bash
   # Only allow specific IPs (optional)
   sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="your-ip" port protocol="tcp" port="5000" accept'
   ```

3. **Regular Updates**
   ```bash
   # Update system regularly
   sudo apt update && sudo apt upgrade -y
   
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

4. **Monitor Logs**
   ```bash
   # Setup log rotation
   sudo nano /etc/logrotate.d/docker-containers
   ```

5. **Backup .env File**
   ```bash
   cp .env .env.backup
   # Store securely, never commit to git
   ```

## 📈 Scaling Tips

### Increase Workers (for more concurrent users)
Edit `Dockerfile`:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "8", ...]
```

### Add More Memory to Container
Edit `docker-compose.yml`:
```yaml
services:
  web:
    mem_limit: 2g
    mem_reservation: 1g
```

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify environment variables: `cat .env`
3. Check Oracle Cloud firewall settings
4. Ensure Spotify redirect URIs are correct
5. Test database: `ls -lh data/`

## 📝 Maintenance Schedule

- **Daily**: Automatic backups at 2 AM
- **Weekly**: Check disk space and logs
- **Monthly**: Update system packages
- **As needed**: Update application code

## 🎉 You're All Set!

Your Music Sync Pro application is now running in production on Oracle Cloud!

Access it at: `https://your-domain.com` or `http://your-server-ip:8080`
