# Music Sync - Web Deployment Guide

## 🚀 Quick Start (Local Development)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt -r requirements-web.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   - Open http://localhost:8080 in your browser
   - Register a new account
   - Connect your Spotify and YouTube Music accounts
   - Start syncing!

---

## 🌐 Oracle Cloud Deployment

### Prerequisites
- Oracle Cloud account with a compute instance
- Domain name (optional, but recommended)
- SSH access to your server

### Step 1: Set Up Server

```bash
# SSH into your Oracle Cloud instance
ssh ubuntu@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone and Configure

```bash
# Clone your repository
git clone https://github.com/yourusername/spotify_to_ytmusic.git
cd spotify_to_ytmusic

# Copy and configure environment
cp .env.example .env
nano .env  # Edit and set secure values

# Generate a secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Configure Firewall

```bash
# Open required ports
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
sudo netfilter-persistent save
```

### Step 4: Deploy with Docker

```bash
# Build and start containers
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### Step 5: Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

---

## 📝 Usage

1. **Register an account** at http://your-domain.com/register

2. **Connect Spotify:**
   - Click "Connect Spotify" on dashboard
   - Authorize the app with Spotify
   - Click "Backup Playlists" to download your data

3. **Connect YouTube Music:**
   - Go to [YouTube Music](https://music.youtube.com) in Firefox
   - Press F12 to open developer tools
   - Go to Network tab and filter by `/browse`
   - Click any request and copy the RAW request headers
   - Paste into the form on the "Connect YouTube Music" page

4. **Start Syncing:**
   - Choose direction (Spotify → YouTube Music or vice versa)
   - Select playlists or liked songs
   - Watch real-time progress!

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key (MUST be unique) | - |
| `DATABASE_URL` | Database connection string | sqlite:///music_sync.db |
| `FLASK_ENV` | Environment mode | development |
| `FLASK_PORT` | Port to run on | 5000 |
| `DB_PASSWORD` | PostgreSQL password | - |

### Database

- **Development:** SQLite (automatic, no setup needed)
- **Production:** PostgreSQL (recommended for multiple users)

To use PostgreSQL, set in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/music_sync
```

---

## 🛠️ Maintenance

### View Logs
```bash
docker-compose logs -f web
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Backup Database
```bash
# SQLite
cp music_sync.db music_sync.db.backup

# PostgreSQL
docker-compose exec db pg_dump -U postgres music_sync > backup.sql
```

---

## 🔐 Security Best Practices

1. **Always use HTTPS** in production
2. **Set a strong SECRET_KEY** (use the generator command)
3. **Use strong database passwords**
4. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt -r requirements-web.txt`
5. **Regular backups** of user data and database
6. **Firewall rules** to restrict unnecessary access

---

## 🐛 Troubleshooting

### Port already in use
```bash
sudo lsof -i :8080
sudo kill -9 <PID>
```

### Docker permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Database errors
```bash
# Reset database (WARNING: deletes all data)
rm music_sync.db
python app.py  # Will recreate database
```

---

## 📱 Accessing from Mobile

Once deployed, you can access the web app from:
- Any computer browser
- iPhone/iPad Safari
- Android Chrome
- Any device with a web browser!

No app installation needed - just visit your domain!

---

## 🎯 Future Features

- [ ] Automatic scheduled syncs
- [ ] Playlist diff viewer
- [ ] Multiple streaming service support (Apple Music, Deezer)
- [ ] Collaborative playlist syncing
- [ ] Mobile app (iOS/Android)

---

## 📄 License

MIT License - See LICENSE file for details
