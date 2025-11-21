# Deploy Using Oracle Cloud Run Command

Since SSH is not working, we'll use Oracle's **Run Command** feature to set up and deploy your application remotely.

## Step 1: Initial Setup (Run Command #1)

1. **Go to Oracle Cloud Console**
   - Navigate to: **Compute** → **Instances**
   - Click on your instance

2. **IMPORTANT: Add Port 2222 to Security List FIRST**
   - Before running the setup script, configure the firewall
   - In the left sidebar under "Resources", click **"Primary VNIC"**
   - Click your **Subnet** name
   - Click **"Security Lists"** → Click your security list name
   - Click **"Add Ingress Rules"**
   - Add this rule:
     - Source Type: `CIDR`
     - Source CIDR: `0.0.0.0/0`
     - IP Protocol: `TCP`
     - Destination Port Range: `2222`
     - Description: `SSH Alternative Port`
   - Click **"Add Ingress Rules"**
   - Also add port `8080` for the web app if not already added

3. **Access Run Command**
   - Go back to your instance
   - In the left sidebar under "Resources", click **"Run command"**
   - Click **"Create run command"**

4. **Configure the command**
   - Command type: **Run shell script**
   - Script name: `setup-instance`
   - Script:
     ```bash
     curl -o /tmp/setup.sh https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/oracle_run_command_setup.sh
     chmod +x /tmp/setup.sh
     sudo /tmp/setup.sh
     ```
   
   **OR** paste the entire contents of `oracle_run_command_setup.sh` directly

4. **Run the command**
   - Click **"Submit run command"**
   - Wait 3-5 minutes for completion
   - Check output for any errors
   - **SSH will now be running on port 2222 instead of 22**

5. **Test SSH connection (optional)**
   ```bash
   ssh -p 2222 -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.21.42
   ```
   If this works, you can use SCP to upload files!

---

## Step 2: Upload Deployment Package

Now we need to get your `music-sync-deploy.tar.gz` file onto the server.

### Method A: Using ngrok (Recommended - 5 minutes)

1. **On your Mac**, open a terminal:
   ```bash
   cd /Users/Ayan/Documents/spotify_to_ytmusic
   python3 -m http.server 8000
   ```
   Keep this running!

2. **Open another terminal**:
   ```bash
   # Install ngrok (one-time only)
   brew install ngrok
   
   # Expose your local server
   ngrok http 8000
   ```

3. **Copy the ngrok URL** from the output (looks like: `https://xxxx-xx-xx.ngrok-free.app`)

4. **Create another Run Command in Oracle Cloud**:
   - Script name: `download-package`
   - Script:
     ```bash
     cd /home/ubuntu/music-sync-app
     wget https://YOUR-NGROK-URL-HERE/music-sync-deploy.tar.gz
     ls -lh music-sync-deploy.tar.gz
     ```
   - Replace `YOUR-NGROK-URL-HERE` with your actual ngrok URL
   - Submit and wait for completion

### Method B: Using SCP (if SSH on port 2222 works)

Once the setup script completes, SSH will be on port 2222:

```bash
# Test connection first
ssh -p 2222 -i /Users/Ayan/Downloads/key2.key ubuntu@140.245.21.42

# If it works, upload the package
scp -P 2222 -i /Users/Ayan/Downloads/key2.key music-sync-deploy.tar.gz ubuntu@140.245.21.42:~/music-sync-app/
```

Note: Capital `-P` for scp, lowercase `-p` for ssh!

If ngrok doesn't work:

1. **Upload to Object Storage**:
   - In Oracle Cloud Console: **Storage** → **Buckets**
   - Create a bucket (e.g., `temp-deploy`)
   - Upload `music-sync-deploy.tar.gz`
   - Make it public (Edit Visibility → Public)
   - Copy the Object URL

2. **Download via Run Command**:
   ```bash
   cd /home/ubuntu/music-sync-app
   wget "YOUR-OBJECT-STORAGE-URL" -O music-sync-deploy.tar.gz
   ```

---

## Step 3: Configure Environment

Create another Run Command:
- Script name: `configure-env`
- Script:
  ```bash
  cd /home/ubuntu/music-sync-app
  
  # Extract the package
  tar -xzf music-sync-deploy.tar.gz
  
  # Create .env file
  cat > .env << 'EOF'
  SECRET_KEY=YOUR_SECRET_KEY_HERE
  SPOTIFY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID_HERE
  SPOTIFY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET_HERE
  FLASK_ENV=production
  EOF
  
  echo "✅ Configuration complete"
  cat .env
  ```

**IMPORTANT**: Replace the placeholder values with your actual credentials:
- `YOUR_SECRET_KEY_HERE` - Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `YOUR_SPOTIFY_CLIENT_ID_HERE` - From Spotify Developer Dashboard
- `YOUR_SPOTIFY_CLIENT_SECRET_HERE` - From Spotify Developer Dashboard

---

## Step 4: Deploy Application

Create another Run Command:
- Script name: `deploy-app`
- Script:
  ```bash
  cd /home/ubuntu/music-sync-app
  chmod +x deploy.sh
  ./deploy.sh
  
  # Wait for startup
  sleep 15
  
  # Check status
  docker ps
  docker logs music-sync-web --tail 50
  ```

---

## Step 5: Verify Deployment

1. **Check if it's running**:
   - Open browser: `http://140.245.21.42:8080`

2. **If you see errors**, create a Run Command:
   ```bash
   docker logs music-sync-web --tail 100
   ```

3. **Update Spotify Redirect URI**:
   - Go to: https://developer.spotify.com/dashboard
   - Click your app
   - Edit Settings → Redirect URIs
   - Add: `http://140.245.21.42:8080/spotify/callback`
   - Save

---

## Useful Run Commands for Management

### Check Application Logs
```bash
docker logs music-sync-web --tail 100 --follow
```

### Restart Application
```bash
cd /home/ubuntu/music-sync-app
docker-compose restart
```

### Stop Application
```bash
cd /home/ubuntu/music-sync-app
docker-compose down
```

### Start Application
```bash
cd /home/ubuntu/music-sync-app
docker-compose up -d
```

### Check Disk Space
```bash
df -h
du -sh /home/ubuntu/music-sync-app/*
```

### Backup Database
```bash
cd /home/ubuntu/music-sync-app
./backup.sh
ls -lh backups/
```

---

## Troubleshooting

### Application won't start
```bash
cd /home/ubuntu/music-sync-app
docker-compose logs
```

### Port 8080 not accessible
Run this command to check firewall:
```bash
sudo iptables -L -n | grep 8080
curl localhost:8080
```

### Need to re-deploy
```bash
cd /home/ubuntu/music-sync-app
docker-compose down
docker-compose up -d --build
```

---

## After Successful Deployment

1. ✅ Access app at: `http://140.245.21.42:8080`
2. ✅ Create your first user account
3. ✅ Connect Spotify OAuth
4. ✅ Upload YouTube Music headers
5. ✅ Start syncing playlists!

---

## Need Help?

If something isn't working:
1. Check logs with Run Command
2. Verify .env file has correct credentials
3. Make sure Spotify redirect URI is updated
4. Check that ports 8080, 80, 443 are open in Security Lists
