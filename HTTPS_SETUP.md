# 🔒 HTTPS Setup Guide

## Prerequisites

Before setting up HTTPS, you need:

1. **A Domain Name** pointing to your server
   - Option A: Buy a domain (Namecheap, GoDaddy, etc.) - $10-15/year
   - Option B: Use a free subdomain service:
     - [Duck DNS](https://www.duckdns.org/) - Free
     - [FreeDNS](https://freedns.afraid.org/) - Free
     - [No-IP](https://www.noip.com/) - Free

2. **DNS Configuration**
   - Create an A record pointing to: `140.245.30.241`
   - Wait 5-60 minutes for DNS propagation

## Quick Setup (Using Let's Encrypt - Free SSL)

### Step 1: Get a Domain

**Option A - Buy a domain:**
1. Go to [Namecheap](https://www.namecheap.com/) or [GoDaddy](https://www.godaddy.com/)
2. Buy a domain (e.g., `mymusicsync.com`)
3. In DNS settings, add an A record:
   - Type: `A`
   - Host: `@` (or your subdomain like `app`)
   - Value: `140.245.30.241`
   - TTL: `Automatic` or `300`

**Option B - Free subdomain (Duck DNS example):**
1. Go to [Duck DNS](https://www.duckdns.org/)
2. Sign in with Google/GitHub
3. Create a subdomain (e.g., `mymusicsync.duckdns.org`)
4. Set IP to: `140.245.30.241`
5. Click "Update IP"

### Step 2: Verify DNS is Working

Wait a few minutes, then test:
```bash
# From your Mac:
nslookup your-domain.com
# or
dig your-domain.com

# Should show: 140.245.30.241
```

### Step 3: Upload SSL Setup Script

```bash
# Upload the SSL setup script
scp -i /Users/Ayan/Downloads/key2.key setup-ssl.sh ubuntu@140.245.30.241:~/
```

### Step 4: Run SSL Setup

```bash
# SSH into server
ssh -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.30.241

# Make script executable
chmod +x setup-ssl.sh

# Run the setup script
sudo ./setup-ssl.sh
```

The script will ask for:
- Your domain name (e.g., `mymusicsync.duckdns.org`)
- Your email (for SSL certificate notifications)

### Step 5: Update Spotify Redirect URI

1. Go to: https://developer.spotify.com/dashboard
2. Click your app → Edit Settings → Redirect URIs
3. **Remove** the old HTTP URI
4. **Add** new HTTPS URI: `https://your-domain.com/spotify/callback`
5. Save

## That's It!

Your app is now accessible at: **https://your-domain.com** 🔒

---

## Alternative: Quick HTTPS without Domain (Cloudflare Tunnel)

If you don't want to buy a domain, you can use Cloudflare Tunnel for free HTTPS:

### Step 1: Install Cloudflare Tunnel

```bash
ssh -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.30.241

# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Authenticate
cloudflared tunnel login
```

### Step 2: Create Tunnel

```bash
# Create tunnel
cloudflared tunnel create music-sync

# Note the tunnel ID shown

# Create config
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: YOUR-TUNNEL-ID
credentials-file: /home/ubuntu/.cloudflared/YOUR-TUNNEL-ID.json

ingress:
  - hostname: your-subdomain.your-domain.com
    service: http://localhost:3000
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel route dns music-sync your-subdomain.your-domain.com
cloudflared tunnel run music-sync
```

---

## Troubleshooting

### SSL Certificate Failed
```bash
# Check if port 80 is open
sudo lsof -i :80

# Check DNS
nslookup your-domain.com

# Try manual certificate
sudo certbot certonly --standalone -d your-domain.com
```

### Nginx Not Starting
```bash
# Check logs
docker logs music_sync_nginx

# Verify certificate paths
ls -la /etc/letsencrypt/live/your-domain.com/
```

### SSL Certificate Expired
```bash
# Renew manually
sudo certbot renew

# Restart nginx
cd /home/ubuntu && docker-compose restart nginx
```

---

## Security Best Practices

After HTTPS is enabled:

1. **Update .env** to force HTTPS redirects
2. **Enable HSTS** (already in config)
3. **Test SSL Configuration:**
   - Go to: https://www.ssllabs.com/ssltest/
   - Enter your domain
   - Should get A or A+ rating

4. **Keep certificates updated:**
   - Auto-renewal is enabled (runs every 12 hours)
   - Check status: `sudo systemctl status certbot.timer`

---

## Cost Summary

- **Free Option**: Duck DNS + Let's Encrypt = $0/year
- **Paid Option**: Domain ($10-15/year) + Let's Encrypt (free)
- **Cloudflare Tunnel**: Free (no domain needed)

**Recommendation**: Start with Duck DNS (free) to test, then buy a custom domain if you like it!
