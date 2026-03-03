# 24/7 Deployment Options

## Option 1: Free Cloud Hosting (Recommended)

### Railway.app (Free Tier)
- 500 hours/month free (enough for 24/7)
- Easy deployment
- Automatic restarts

**Setup:**
1. Create account at https://railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Login: `railway login`
4. Deploy: `railway up`
5. Set environment variables in Railway dashboard

### Render.com (Free Tier)
- Free tier available
- Auto-deploys from GitHub
- Sleeps after 15 min inactivity (not ideal for this)

### fly.io (Free Tier)
- 3 shared VMs free
- Good for 24/7 bots
- More technical setup

**Setup for fly.io:**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

## Option 2: Android Phone (Termux)

Run the bot on your Android phone using Termux - completely free!

**Setup:**
1. Install Termux from F-Droid (not Play Store)
2. Open Termux and run:
```bash
# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python

# Install git
pkg install git

# Clone your bot (or copy files)
# Install dependencies
pip install requests plyer

# Run bot
python sniper.py
```

**Keep it running:**
```bash
# Install tmux to keep running in background
pkg install tmux

# Start tmux session
tmux new -s sniper

# Run bot
python sniper.py

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t sniper
```

**Important for Android:**
- Disable battery optimization for Termux
- Keep phone plugged in or use battery saver wisely
- Disable desktop notifications (they won't work on Android)

## Option 3: Oracle Cloud (Always Free)

Oracle offers always-free VMs that are perfect for this!

**Free Tier:**
- 2 AMD VMs (1/8 OCPU, 1GB RAM each)
- OR 4 ARM VMs (1 OCPU, 6GB RAM each)
- Always free, no credit card expiry

**Setup:**
1. Create account at https://cloud.oracle.com
2. Create a VM instance (Ubuntu)
3. SSH into the VM
4. Install Python and dependencies:
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install requests
```
5. Upload your bot files
6. Run with systemd (see below)

## Option 4: Google Cloud Run (Free Tier)

- 2 million requests/month free
- Not ideal for continuous polling, but works

## Running as a Service (Linux/Oracle Cloud)

Create a systemd service to auto-restart:

**Create `/etc/systemd/system/csfloat-sniper.service`:**
```ini
[Unit]
Description=CSFloat Sniper Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/csfloat-sniper
ExecStart=/usr/bin/python3 /path/to/csfloat-sniper/sniper.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable csfloat-sniper
sudo systemctl start csfloat-sniper
sudo systemctl status csfloat-sniper
```

## Recommended Setup

**Best Free Option: Oracle Cloud Always Free VM**
- Truly free forever
- Reliable 24/7 uptime
- Easy to set up
- Can run multiple bots

**Easiest Option: Android Phone with Termux**
- No signup required
- Works immediately
- Use old phone you're not using
- Completely free

**Simplest Cloud: Railway.app**
- Easiest deployment
- Good free tier
- May need to upgrade after free hours

## Configuration for Cloud/Android

Update `config.json` for cloud deployment:
```json
{
  "notifications": {
    "desktop": false,  // Disable on cloud/Android
    "discord": true,   // Use Discord for alerts
    "log_file": "snipes.log"
  }
}
```

## Monitoring

Check if bot is running:
```bash
# Linux/Cloud
ps aux | grep sniper.py

# Android (Termux)
tmux list-sessions
```

View logs:
```bash
tail -f snipes.log
```

## Tips

1. **Disable desktop notifications** on cloud/Android (set to false)
2. **Use Discord** for all alerts
3. **Set check_interval to 20-30 seconds** to avoid rate limits
4. **Monitor the logs** regularly
5. **Keep API key secure** - don't commit to public repos
