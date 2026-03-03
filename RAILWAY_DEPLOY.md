# Deploy to Railway.app

## Quick Start (No GitHub)

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Deploy:**
```bash
railway init
railway up
```

4. **Set your config as environment variables:**
```bash
railway variables set CSFLOAT_API_KEY="your_api_key_here"
railway variables set DISCORD_WEBHOOK_URL="your_webhook_url"
railway variables set MIN_DISCOUNT="18"
railway variables set MAX_PRICE="10000"
railway variables set CHECK_INTERVAL="20"
```

Done! Your bot is now running 24/7.

## Deploy from GitHub (Recommended for Updates)

### Step 1: Prepare Your Repo

**IMPORTANT:** Don't commit your API keys!

1. Make sure `.gitignore` includes `config.json`
2. Create a private GitHub repo
3. Push your code:

```bash
git init
git add .
git commit -m "CSFloat sniper bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/csfloat-sniper.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `csfloat-sniper` repo
5. Railway will auto-detect Python and deploy

### Step 3: Configure Environment Variables

In Railway dashboard, go to Variables tab and add:

```
CSFLOAT_API_KEY=your_api_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
MIN_DISCOUNT=18
MAX_PRICE=10000
CHECK_INTERVAL=20
DESKTOP_NOTIFICATIONS=false
DISCORD_NOTIFICATIONS=true
```

### Step 4: Verify Deployment

Check the logs in Railway dashboard to see if bot is running.

## Using config.json Instead (Simpler)

If you don't want to use environment variables:

1. Keep `config.json` in your repo
2. Make repo **private** on GitHub
3. Deploy normally
4. Railway will use your config.json

**Security Note:** Private repos are safe, but environment variables are more secure.

## Monitoring

- **View logs:** Railway dashboard → Deployments → Logs
- **Check status:** Look for "CSFloat Sniper Bot Started" message
- **Discord alerts:** You'll get notifications when snipes are found

## Troubleshooting

**Bot not starting?**
- Check logs in Railway dashboard
- Verify `Procfile` exists with: `worker: python sniper.py`
- Make sure `requirements.txt` is correct

**No notifications?**
- Check Discord webhook URL is correct
- Verify `DISCORD_NOTIFICATIONS=true`
- Check Railway logs for errors

**Rate limited?**
- Increase `CHECK_INTERVAL` to 30 or 60 seconds
- Check logs for "429" errors

## Cost

Railway free tier includes:
- $5 credit/month
- ~500 hours of runtime
- Should be enough for 24/7 operation

If you exceed free tier, consider:
- Oracle Cloud Always Free (truly free forever)
- Android phone with Termux (free)
