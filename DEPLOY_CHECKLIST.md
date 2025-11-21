# 🚀 Oracle Cloud Deployment Checklist

## 📦 What You Have Ready
- ✅ Deployment package: `music-sync-deploy.tar.gz` (9.1MB)
- ✅ All deployment scripts ready
- ✅ Docker configuration ready
- ✅ Premium UI with "On Fire" design
- ✅ **Application runs on port 8080**

---

## 🎯 Step-by-Step Deployment

### Step 1: Prepare Oracle Cloud Instance

**What you need:**
- [ ] Oracle Cloud account login
- [ ] Compute instance created (Ubuntu 20.04+)
- [ ] Instance public IP address: `___________________`
- [ ] SSH private key file (if using key authentication)

**Connect to your server:**
```bash
ssh ubuntu@YOUR_SERVER_IP
# or
ssh -i /path/to/your-key.pem ubuntu@YOUR_SERVER_IP
```

---

### Step 2: Install Docker on Server

**Run on your Oracle Cloud server:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

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

# IMPORTANT: Log out and back in for docker group to take effect
exit
```

Then reconnect: `ssh ubuntu@YOUR_SERVER_IP`

---

### Step 3: Upload Your Application

**From your Mac terminal** (new terminal window):
```bash
cd /Users/Ayan/Documents/spotify_to_ytmusic

# Upload the deployment package
scp music-sync-deploy.tar.gz ubuntu@YOUR_SERVER_IP:~/
```

---

### Step 4: Extract and Setup on Server

**Back on your Oracle server:**
```bash
# Create application directory
mkdir -p ~/spotify_to_ytmusic
cd ~/spotify_to_ytmusic

# Extract files
tar -xzf ~/music-sync-deploy.tar.gz

# Make scripts executable
chmod +x *.sh

# Verify files
ls -la
```

---

### Step 5: Configure Environment Variables

```bash
cd ~/spotify_to_ytmusic

# Copy example env file
cp .env.example .env

# Generate a new SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env

# Edit the .env file
nano .env
```

**Update these values:**
```bash
# Press Ctrl+W to search, then update:
SPOTIFY_CLIENT_ID=329e873b7a9f45a4a8128770e084e27c
SPOTIFY_CLIENT_SECRET=8f1b93abb7cd4a808adfa6e25af1977f
FLASK_ENV=production
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

### Step 6: Open Firewall Ports

**A) In Oracle Cloud Console (Web Browser):**
1. Go to: https://cloud.oracle.com
2. Menu → Networking → Virtual Cloud Networks
3. Click your VCN name
4. Click "Security Lists"
5. Click "Default Security List"
6. Click "Add Ingress Rules"
7. Add these 3 rules:

**Rule 1 - HTTP:**
- Source CIDR: `0.0.0.0/0`
- Destination Port: `80`
- Description: `HTTP`

**Rule 2 - HTTPS:**
- Source CIDR: `0.0.0.0/0`
- Destination Port: `443`
- Description: `HTTPS`

**Rule 3 - Flask App:**
- Source CIDR: `0.0.0.0/0`
- Destination Port: `8080`
- Description: `Flask App`

**B) On Your Server:**
```bash
# Open ports in server firewall
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT

# Save rules (install if needed)
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
```

---

### Step 7: Deploy the Application!

```bash
cd ~/spotify_to_ytmusic
./deploy.sh
```

**This will:**
- ✅ Build Docker container
- ✅ Start the application
- ✅ Show you the status

**Wait for:** "✅ Deployment successful!"

---

### Step 8: Verify It's Running

```bash
# Check if container is running
docker ps

# Test locally
curl http://localhost:8080

# View logs
docker-compose logs -f
```

**Access your app:**
- Open browser: `http://YOUR_SERVER_IP:8080`
- You should see the login/register page with the premium "On Fire" design! 🔥

---

### Step 9: Update Spotify Redirect URI

1. Go to: https://developer.spotify.com/dashboard
2. Click on your app
3. Click "Edit Settings"
4. Under "Redirect URIs", add:
   ```
   http://YOUR_SERVER_IP:8080/spotify/callback
   ```
5. Click "Add"
6. Click "Save" at the bottom

---

### Step 10: Test Your App!

1. Go to `http://YOUR_SERVER_IP:8080`
2. Register a new account
3. Login
4. Connect Spotify (test OAuth)
5. Connect YouTube Music
6. Try a sync!

---

## 🎉 Success Checklist

- [ ] Docker installed on server
- [ ] Files uploaded and extracted
- [ ] .env configured with Spotify credentials
- [ ] Firewall ports opened (Oracle + server)
- [ ] Application deployed successfully
- [ ] App accessible at http://YOUR_IP:8080
- [ ] Spotify redirect URI updated
- [ ] Can register and login
- [ ] Spotify connection works
- [ ] YouTube Music connection works
- [ ] Sync works!

---

## 🔧 Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart app
docker-compose restart

# Stop app
docker-compose down

# Start app
docker-compose up -d

# Backup database
./backup.sh

# Setup automatic backups (daily at 2 AM)
./setup-cron.sh
```

---

## 🆘 Troubleshooting

**Can't access from internet?**
- Double-check Oracle Cloud Security Lists
- Check server firewall: `sudo iptables -L -n`
- Try: `curl localhost:8080` on server

**Container won't start?**
```bash
docker-compose logs
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Port 8080 already in use?**
```bash
sudo lsof -i :8080
sudo kill -9 <PID>
```

---

## 📝 What to Tell Me

When ready to start, provide:

1. **Your Oracle Cloud server IP:** `___________________`
2. **SSH works?** (yes/no): `___________________`
3. **Got the Spotify credentials?** (yes/no): `___________________`

Let's deploy! 🚀
