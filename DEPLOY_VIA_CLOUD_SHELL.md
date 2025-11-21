# Deploy via Oracle Cloud Shell (SSH Alternative)

Since direct SSH is blocked, we'll use Oracle Cloud Shell and a temporary web server to transfer files.

## Method 1: Simple HTTP Upload (Recommended)

### Step 1: Start a temporary web server on your Mac
```bash
cd /Users/Ayan/Documents/spotify_to_ytmusic
python3 -m http.server 8000
```
Keep this terminal open!

### Step 2: Expose your local server to the internet
In a new terminal, install and run ngrok:
```bash
# Install ngrok (one-time)
brew install ngrok

# Expose port 8000
ngrok http 8000
```

You'll see output like:
```
Forwarding    https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

Copy that HTTPS URL!

### Step 3: Access Oracle Cloud Shell
1. Go to Oracle Cloud Console: https://cloud.oracle.com
2. Click the **Developer Tools icon** (>_) in the top-right corner
3. Click **Cloud Shell** - it opens at the bottom of your browser

### Step 4: Download and deploy in Cloud Shell
In the Cloud Shell terminal, run:
```bash
# SSH to your instance
ssh -i ~/.ssh/your-key ubuntu@140.245.21.42

# If that doesn't work, you may need to upload your SSH key first:
# (Upload key2.key via Cloud Shell's upload feature)
# chmod 600 key2.key
# ssh -i ./key2.key ubuntu@140.245.21.42
```

### Step 5: Once connected to your instance
```bash
# Download the deployment package (replace with your ngrok URL)
wget https://xxxx-xx-xx-xx-xx.ngrok-free.app/music-sync-deploy.tar.gz

# Extract
tar -xzf music-sync-deploy.tar.gz

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for docker group to take effect
exit
# SSH back in
ssh -i ./key2.key ubuntu@140.245.21.42

# Configure environment
cd ~/
nano .env
# Add your Spotify credentials and SECRET_KEY
# Press Ctrl+O to save, Ctrl+X to exit

# Deploy!
chmod +x deploy.sh
./deploy.sh
```

---

## Method 2: If Cloud Shell can't SSH either

If Cloud Shell also can't SSH to your instance, then **port 22 is definitely blocked at the Oracle Cloud level**.

### Fix the firewall issue:

1. **Go to your instance in Oracle Cloud Console**
   - Compute → Instances → Click your instance name

2. **Find the subnet settings**
   - Under "Primary VNIC" → Click the Subnet name

3. **Edit Security List**
   - Click "Default Security List" or your security list name
   - Click "Add Ingress Rules"
   - Fill in:
     - Source Type: `CIDR`
     - Source CIDR: `0.0.0.0/0`
     - IP Protocol: `TCP`
     - Source Port Range: `All`
     - Destination Port Range: `22`
     - Description: `SSH Access`
   - Click "Add Ingress Rules"

4. **Check for Network Security Groups**
   - Go back to your instance
   - Under "Primary VNIC" → Click "Network Security Groups"
   - If any NSGs are attached, you need to add the same rule there too

5. **Check Instance Firewall (via Serial Console)**
   - Instance Details → Resources → Console Connection
   - If no console connection exists, click "Create Console Connection"
   - Launch the Cloud Shell
   - Connect with the provided command
   - Once in, check: `sudo iptables -L -n | grep 22`
   - If port 22 is blocked, run: `sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT`

---

## Quick Test After Fixing Firewall

From Cloud Shell:
```bash
nc -zv 140.245.21.42 22
```

If it says "Connection succeeded", then SSH should work!

---

## Need Help?
If you're still stuck, let me know what error message you see and we'll troubleshoot together.
