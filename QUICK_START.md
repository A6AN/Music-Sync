# 🚀 QUICK START - Deploy to Oracle Cloud

## 📦 What You Have

Your deployment package is ready with:
- ✅ `Dockerfile` - Production container setup
- ✅ `docker-compose.yml` - Simple one-command deployment
- ✅ `deploy.sh` - Automated deployment script
- ✅ `backup.sh` - Database backup script
- ✅ `restore.sh` - Database restore script
- ✅ `setup-cron.sh` - Automatic backup scheduler
- ✅ `nginx.conf` - Reverse proxy configuration
- ✅ `DEPLOY_GUIDE.md` - Detailed deployment instructions

## 🎯 Steps to Deploy (Simple Version)

### 1. Prepare Your Oracle Cloud Server

SSH into your server and run:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in
exit
```

### 2. Upload Your Files

**From your Mac:**
```bash
cd /Users/Ayan/Documents/spotify_to_ytmusic

# Create archive (excluding unnecessary files)
tar -czf music-sync.tar.gz \
  --exclude='.git' \
  --exclude='*.db' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.bak' \
  --exclude='data' \
  --exclude='backups' \
  .

# Upload to server (replace with your IP)
scp music-sync.tar.gz ubuntu@YOUR_SERVER_IP:~/
```

**On your server:**
```bash
mkdir -p ~/spotify_to_ytmusic
cd ~/spotify_to_ytmusic
tar -xzf ~/music-sync.tar.gz
chmod +x *.sh
```

### 3. Configure Environment

```bash
cd ~/spotify_to_ytmusic

# Copy env example
cp .env.example .env

# Generate secret key and edit config
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
nano .env
```

**Update in .env:**
- `SPOTIFY_CLIENT_ID=your_id_here`
- `SPOTIFY_CLIENT_SECRET=your_secret_here`

### 4. Open Firewall Ports

**In Oracle Cloud Console:**
1. Go to: Networking → Virtual Cloud Networks → Your VCN
2. Click on: Security Lists → Default Security List
3. Add Ingress Rules:
   - Port 80 (HTTP)
   - Port 443 (HTTPS)  
   - Port 8080 (Flask)
   - Source: 0.0.0.0/0

**On the server:**
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
sudo netfilter-persistent save
```

### 5. Deploy!

```bash
./deploy.sh
```

That's it! Your app is now running at: `http://YOUR_SERVER_IP:8080`

## 🔐 Update Spotify Redirect URI

Go to: https://developer.spotify.com/dashboard

Add redirect URI:
```
http://YOUR_SERVER_IP:8080/spotify/callback
```

## 📊 Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart app
docker-compose restart

# Stop app
docker-compose down

# Backup database
./backup.sh

# Setup automatic backups
./setup-cron.sh
```

## 🌐 Optional: Setup Domain with HTTPS

### 1. Point Your Domain

In your domain registrar, add an A record:
```
@ → YOUR_SERVER_IP
```

### 2. Install Nginx + SSL

```bash
# Install Nginx
sudo apt install -y nginx

# Copy config
sudo cp nginx.conf /etc/nginx/sites-available/music-sync
sudo nano /etc/nginx/sites-available/music-sync
# Replace 'your-domain.com' with your actual domain

# Enable site
sudo ln -s /etc/nginx/sites-available/music-sync /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Now access at: `https://yourdomain.com` 🎉

## 💾 Backup Strategy

**Automatic (Recommended):**
```bash
./setup-cron.sh
```
This backs up database daily at 2 AM.

**Manual:**
```bash
./backup.sh
```

**Restore:**
```bash
./restore.sh
```

Backups are stored in: `./backups/`

## 🆘 Troubleshooting

**App won't start?**
```bash
docker-compose logs
```

**Port already in use?**
```bash
sudo lsof -i :8080
sudo kill -9 PID
```

**Can't access from internet?**
- Check Oracle Cloud Security Lists
- Check server firewall: `sudo iptables -L -n`

**Database issues?**
```bash
./restore.sh
```

## 📝 What You Need to Give Me

To deploy this, you'll need to provide:

1. **Oracle Cloud Server IP Address**
2. **SSH credentials** (username/password or key)
3. **Your domain name** (if you have one)
4. **Spotify App Credentials**:
   - Client ID
   - Client Secret

That's all! I can help guide you through each step.

## 🎯 Success Checklist

- [ ] Docker installed on server
- [ ] Files uploaded to server
- [ ] .env configured with Spotify credentials
- [ ] Firewall ports opened (Oracle Console + server)
- [ ] Spotify redirect URI updated
- [ ] Run ./deploy.sh
- [ ] App accessible at http://YOUR_IP:8080
- [ ] Setup automatic backups
- [ ] (Optional) Configure domain + HTTPS

---

**Ready to deploy? Let me know your Oracle Cloud server IP and we'll get started! 🚀**
